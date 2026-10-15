"""Optional YouTube Live chat reader.

Uses the official liveChatMessages.list endpoint when YOUTUBE_API_KEY and
YOUTUBE_LIVE_CHAT_ID are configured. It never changes the match score.
"""
import asyncio
import os
import re
import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import httpx


COMMANDS = {"placar", "jogador", "pergunta", "narrar", "escalação", "escalacao"}


def clean_text(value: Any, limit: int = 240) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


class YouTubeLiveChat:
    def __init__(self, state, broadcast):
        self.state = state
        self.broadcast = broadcast
        self.task = None
        self.next_page = ""
        self.seen: set[str] = set()
        self.last_user: dict[str, float] = {}
        self.mentions: dict[str, dict[str, Any]] = {}
        self.info = {"enabled": False, "connected": False, "messages": 0, "error": None}
        self.state["youtube_chat"] = dict(self.info)

    def configured(self):
        return bool(os.getenv("YOUTUBE_API_KEY", "").strip() and os.getenv("YOUTUBE_LIVE_CHAT_ID", "").strip())

    def status(self):
        return {**self.info, "configured": self.configured(), "chat_id": bool(os.getenv("YOUTUBE_LIVE_CHAT_ID", "").strip()), "top_players": self.top_players()}

    def _player_names(self):
        names = []
        for lineup in (self.state.get("lineups") or {}).values():
            for player in (lineup or {}).get("starters", []) + (lineup or {}).get("bench", []):
                name = clean_text(player.get("name", ""), 80)
                if len(name) >= 3:
                    names.append(name)
        return names

    def track_mentions(self, text: str):
        folded = text.casefold()
        for name in self._player_names():
            if name.casefold() not in folded:
                continue
            entry = self.mentions.setdefault(name, {"name": name, "count": 0})
            entry["count"] += 1

    def top_players(self):
        return sorted(self.mentions.values(), key=lambda item: (-item["count"], item["name"].casefold()))[:3]

    def make_event(self, text: str, author: str, kind: str = "event"):
        return {
            "id": "youtube:" + str(uuid4()), "minute": self.state.get("minute", 0),
            "icon": "💬", "kind": kind, "text": text, "player": "", "team": "",
            "speak": True, "urgent": False, "source": {"name": "YouTube Live Chat"},
            "author": author, "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def response_for(self, message: str, author: str):
        raw = clean_text(message)
        if not raw.startswith("!"):
            return None
        parts = raw[1:].split(maxsplit=1)
        command = parts[0].casefold() if parts else ""
        argument = parts[1] if len(parts) > 1 else ""
        if command not in COMMANDS:
            return None
        now = time.monotonic()
        if now - self.last_user.get(author, 0) < 30:
            return None
        self.last_user[author] = now
        if command == "placar":
            h, a = self.state["home"], self.state["away"]
            return f"Placar: {h['name']} {h['score']}, {a['name']} {a['score']}. {self.state.get('status', '')}."
        if command in {"escalação", "escalacao"}:
            return "As escalações e os jogadores em campo estão disponíveis no painel da transmissão."
        if command == "jogador":
            top = ", ".join(f"{item['name']} ({item['count']} menções)" for item in self.top_players()) or "ainda não há menções suficientes"
            return f"Os três jogadores mais comentados são: {top}. Pedido recebido sobre {argument or 'o jogador'}; vou usar apenas dados confirmados."
        if command == "pergunta":
            return f"Pergunta recebida: {argument or 'sem texto'}. A resposta será baseada nos dados disponíveis da partida."
        if command == "narrar":
            return "Pedido de narração recebido. Os lances importantes têm prioridade na fila."
        return None

    async def poll(self):
        key = os.getenv("YOUTUBE_API_KEY", "").strip()
        chat_id = os.getenv("YOUTUBE_LIVE_CHAT_ID", "").strip()
        params = {"liveChatId": chat_id, "part": "snippet,authorDetails", "maxResults": 200, "key": key}
        if self.next_page:
            params["pageToken"] = self.next_page
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get("https://www.googleapis.com/youtube/v3/liveChat/messages", params=params)
            response.raise_for_status()
            return response.json()

    async def loop(self):
        self.info.update(enabled=True)
        while self.configured():
            try:
                data = await self.poll()
                self.next_page = data.get("nextPageToken", self.next_page)
                for item in data.get("items", []):
                    message_id = str(item.get("id", ""))
                    if not message_id or message_id in self.seen:
                        continue
                    self.seen.add(message_id)
                    snippet = item.get("snippet", {})
                    author = clean_text(item.get("authorDetails", {}).get("displayName", "espectador"), 80)
                    text = clean_text(snippet.get("displayMessage", ""))
                    self.track_mentions(text)
                    response = self.response_for(text, author)
                    self.info["messages"] += 1
                    if response:
                        self.state["events"] = ([self.make_event(response, author)] + self.state.get("events", []))[:6]
                self.info.update(connected=True, error=None)
                self.state["youtube_chat"] = self.status()
                await self.broadcast()
                await asyncio.sleep(max(2, int(data.get("pollingIntervalMillis", 5000) / 1000)))
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.info.update(connected=False, error=clean_text(exc, 180))
                self.state["youtube_chat"] = self.status()
                await self.broadcast()
                await asyncio.sleep(10)
        self.info.update(enabled=False, connected=False)
        self.state["youtube_chat"] = self.status()

    async def start(self):
        if not self.configured() or self.task and not self.task.done():
            return self.status()
        self.task = asyncio.create_task(self.loop())
        return self.status()

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        self.info.update(enabled=False, connected=False)
        self.state["youtube_chat"] = self.status()

    def install(self, app):
        @app.get("/api/youtube/status")
        async def status():
            return self.status()

        @app.get("/api/youtube/top-players")
        async def top_players():
            return {"players": self.top_players()}

        @app.post("/api/youtube/start")
        async def start():
            return await self.start()

        @app.post("/api/youtube/stop")
        async def stop():
            await self.stop()
            return self.status()
