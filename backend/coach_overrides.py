"""Local coach overrides, saved per team and independent of provider refreshes."""
import json
import re
from pathlib import Path
from typing import Literal
from fastapi import HTTPException
from pydantic import BaseModel, Field
from backend.team_names import canonical_name


def team_key(state, side):
    team = state.get(side) or {}
    return canonical_name(team.get('source_name') or team.get('name') or '')


class CoachOverride(BaseModel):
    side: Literal['home', 'away']
    team: str = Field(min_length=1, max_length=200)
    name: str = Field(default='', max_length=120)
    photo: str = Field(default='', max_length=200)
    reset: bool = False


class CoachOverrides:
    def __init__(self, base, state, broadcast):
        self.base, self.state, self.broadcast = Path(base), state, broadcast
        self.path = self.base / 'coach_overrides.json'
        try:
            saved = json.loads(self.path.read_text(encoding='utf-8'))
            self.saved = {k: v for k, v in saved.items() if isinstance(k, str) and isinstance(v, dict)
                          and isinstance(v.get('name'), str) and 0 < len(v['name']) <= 120
                          and (not v.get('photo') or self.valid_photo(v['photo']))}
        except (OSError, ValueError, AttributeError):
            self.saved = {}
        self.observe()

    def valid_photo(self, value):
        return isinstance(value, str) and bool(re.fullmatch(r'/static/uploads/[a-f0-9]{64}\.(png|jpg|webp)', value)) and (self.base / value.lstrip('/')).is_file()

    def observe(self):
        self.state['coach_overrides'] = {side: {**self.saved[key], 'source': 'Cadastro manual'}
            for side in ('home', 'away') if (key := team_key(self.state, side)) in self.saved}

    def install(self, app):
        @app.post('/api/coaches/manual')
        async def save(payload: CoachOverride):
            key = team_key(self.state, payload.side)
            if not key or canonical_name(payload.team) != key:
                raise HTTPException(409, 'O time mudou. Selecione o técnico novamente.')
            updated = self.saved.copy()
            if payload.reset:
                updated.pop(key, None)
            else:
                name = payload.name.strip()
                if not name:
                    raise HTTPException(400, 'Informe o nome do técnico.')
                if payload.photo and not self.valid_photo(payload.photo):
                    raise HTTPException(400, 'Envie a foto pelo seletor de imagens do painel.')
                updated[key] = {'name': name, 'photo': payload.photo}
            try:
                temp = self.path.with_suffix('.tmp')
                temp.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding='utf-8')
                temp.replace(self.path)
            except OSError as exc:
                raise HTTPException(500, 'Não foi possível salvar o técnico.') from exc
            self.saved = updated
            self.observe()
            await self.broadcast()
            return {'saved': True}
