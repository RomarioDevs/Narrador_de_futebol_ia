import os
import unittest
from unittest.mock import patch

from backend.news_context import NewsContext
from backend.youtube_live import YouTubeLiveChat


class ContextFeatureTests(unittest.TestCase):
    def setUp(self):
        self.state = {
            "home": {"name": "Mandante", "score": 0},
            "away": {"name": "Visitante", "score": 0},
            "lineups": {"home": {"starters": [{"name": "Pedro"}], "bench": []}, "away": {"starters": [{"name": "João"}], "bench": []}},
        }

    def test_top_three_mentions_are_sorted(self):
        chat = YouTubeLiveChat(self.state, lambda: None)
        for message in ("Pedro foi bem", "João também", "Pedro", "Pedro", "João", "Outro"):
            chat.track_mentions(message)
        self.assertEqual([item["name"] for item in chat.top_players()], ["Pedro", "João"])
        self.assertEqual(chat.top_players()[0]["count"], 3)

    def test_news_is_optional_without_key(self):
        context = NewsContext(self.state)
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(context.configured())


if __name__ == "__main__":
    unittest.main()
