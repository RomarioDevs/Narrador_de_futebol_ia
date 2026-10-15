import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.coach_overrides import CoachOverrides
from backend.club_context import ClubContext, player_facts


class CoachOverrideTests(unittest.TestCase):
    def test_save_photo_persistence_side_change_and_reset(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            image = base / 'static' / 'uploads' / ('a'*64 + '.png')
            image.parent.mkdir(parents=True)
            image.write_bytes(b'validated upload placeholder')
            state = {'home': {'name': 'País de Gales', 'source_name': 'Wales'}, 'away': {'name': 'Denmark'}}
            service = CoachOverrides(base, state, AsyncMock())
            app = FastAPI();service.install(app)
            with TestClient(app) as client:
                payload = {'side': 'home', 'team': 'Wales', 'name': 'Craig Bellamy', 'photo': '/static/uploads/' + image.name}
                self.assertEqual(client.post('/api/coaches/manual', json=payload).status_code, 200)
                self.assertEqual(state['coach_overrides']['home']['name'], 'Craig Bellamy')
                self.assertNotIn('away', state['coach_overrides'])
                reloaded = CoachOverrides(base, state, AsyncMock())
                self.assertEqual(reloaded.saved, service.saved)
                state['home'], state['away'] = state['away'], state['home']
                service.observe()
                self.assertIn('away', state['coach_overrides'])
                self.assertEqual(client.post('/api/coaches/manual', json=payload).status_code, 409)
                payload.update(side='away', photo='https://example.com/photo.png')
                self.assertEqual(client.post('/api/coaches/manual', json=payload).status_code, 400)
                self.assertEqual(client.post('/api/coaches/manual', json={**payload, 'reset': True}).status_code, 200)
                self.assertEqual(state['coach_overrides'], {})

    def test_catalog_name_translation_and_structured_coach(self):
        row = {'idPlayer': '1', 'idTeam': '2', 'strTeam': 'Wales', 'strSport': 'Soccer',
               'strPosition': 'Manager', 'strPlayer': 'Craig Bellamy', 'strThumb': 'https://example.com/c.png'}
        facts = player_facts([row], {}, 'away', 'ESPN', '2')
        self.assertIn('País de Gales', facts[0]['text'])
        self.assertEqual(facts[0]['coach']['photo'], row['strThumb'])
        state = {'source': 'ESPN', 'home': {'name': 'Dinamarca'}, 'away': {'name': 'País de Gales', 'source_name': 'Wales'}}
        service = ClubContext()
        service.match_team = AsyncMock(side_effect=[[], facts])
        app = FastAPI();broadcast = AsyncMock();service.install(app, state, broadcast)
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/narration/context').status_code, 200)
        self.assertEqual(state['catalog_coaches']['away']['name'], 'Craig Bellamy')
        broadcast.assert_awaited_once()
        state['away']['name'] = 'Other'
        service.observe(state)
        self.assertEqual(state['catalog_coaches'], {})
