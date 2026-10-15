"""Optional, attributed news context for the local brain.

News is never treated as a live event. It is fetched on demand and exposed as
facts with title, source and publication date for the local planner.
"""
from datetime import datetime, timedelta, timezone
import os
import re
from typing import Any

import httpx


class NewsContext:
    def __init__(self, state):
        self.state = state
        self.state["news_context"] = {"configured": self.configured(), "articles": [], "facts": [], "error": None}

    def configured(self):
        return bool(os.getenv("NEWS_API_KEY", "").strip())

    def status(self):
        return self.state.get("news_context", {})

    @staticmethod
    def clean(value, limit=500):
        return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]

    async def fetch(self, days=3):
        days = 7 if int(days) >= 7 else 3
        key = os.getenv("NEWS_API_KEY", "").strip()
        if not key:
            self.state["news_context"] = {"configured": False, "articles": [], "facts": [], "error": "Configure NEWS_API_KEY no arquivo .env."}
            return self.status()
        names = [self.state.get(side, {}).get("name", "") for side in ("home", "away")]
        names = [name for name in names if len(name) >= 3 and name not in {"Mandante", "Visitante"}]
        if not names:
            raise ValueError("Carregue uma partida antes de buscar notícias.")
        query = " OR ".join(f'"{name}"' for name in names)
        params = {"q": query, "from": (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat(), "sortBy": "publishedAt", "pageSize": 20, "language": "pt", "apiKey": key}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get("https://newsapi.org/v2/everything", params=params)
            response.raise_for_status()
            data = response.json()
        articles = []
        for item in data.get("articles", []):
            title = self.clean(item.get("title"), 220)
            url = self.clean(item.get("url"), 500)
            source = self.clean((item.get("source") or {}).get("name"), 100)
            published = self.clean(item.get("publishedAt"), 40)
            if not title or not url or not source:
                continue
            articles.append({"title": title, "url": url, "source": source, "published_at": published, "description": self.clean(item.get("description"), 300)})
        facts = [{"id": "news:" + str(index), "text": f"Notícia recente: {item['title']} — fonte {item['source']}, publicada em {item['published_at'] or 'data não informada'}.", "source": {"name": item["source"], "url": item["url"]}} for index, item in enumerate(articles)]
        self.state["news_context"] = {"configured": True, "days": days, "updated_at": datetime.now(timezone.utc).isoformat(), "articles": articles[:12], "facts": facts[:12], "error": None}
        return self.status()

    def install(self, app):
        @app.get("/api/context/news")
        async def news(days: int = 3):
            return await self.fetch(days)

        @app.get("/api/context/status")
        async def status():
            return self.status()
