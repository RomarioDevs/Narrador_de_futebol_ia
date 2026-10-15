import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.player_photos import PlayerPhotos


class PlayerPhotoTests(unittest.TestCase):
    def test_save_reload_restore_and_reject_stale_player_or_path(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            uploads = base / 'static' / 'uploads'
            uploads.mkdir(parents=True)
            name = 'a' * 64 + '.png'
            (uploads / name).write_bytes(b'fixture')
            url = '/static/uploads/' + name
            state = {'source': 'ESPN', 'home': {'name': 'Home Team'}, 'away': {'name': 'Away Team'},
                     'lineups': {'home': {'starters': [{'id': '1', 'name': 'Player'}]}}}
            service = PlayerPhotos(base, state, AsyncMock())
            app = FastAPI()
            service.install(app)
            with TestClient(app) as client:
                key = 'home team|player'
                self.assertEqual(client.post('/api/players/photo', json={'key': key, 'url': url}).status_code, 200)
                self.assertEqual(PlayerPhotos(base, {}, AsyncMock()).photos[key], url)
                state['source'] = 'GE'
                state['lineups']['home']['starters'] = [{'id': '99', 'name': 'Player'}]
                self.assertEqual(client.post('/api/players/photo', json={'key': key, 'url': url}).status_code, 200)
                self.assertEqual(client.post('/api/players/photo', json={'key': 'home team|other', 'url': url}).status_code, 409)
                for bad in ('/static/uploads/../../secret.png', 'https://example.com/photo.png', '/static/uploads/' + 'b'*64 + '.png'):
                    self.assertEqual(client.post('/api/players/photo', json={'key': key, 'url': bad}).status_code, 400)
                self.assertEqual(client.post('/api/players/photo', json={'key': key, 'url': ''}).status_code, 200)
                self.assertEqual(PlayerPhotos(base, {}, AsyncMock()).photos, {})
