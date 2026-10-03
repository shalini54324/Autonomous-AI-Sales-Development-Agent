from __future__ import annotations
import json
from typing import TypeVar, Type
from pydantic import BaseModel, ValidationError
from app.config import settings

T=TypeVar("T", bound=BaseModel)

class AIUnavailable(RuntimeError): pass

class OpenAIService:
    def __init__(self, api_key: str | None=None, model: str | None=None):
        self.api_key=(api_key if api_key is not None else settings.openai_api_key).strip()
        self.model=model or settings.openai_model
        self._client=None

    @property
    def available(self): return bool(self.api_key)

    def _client_obj(self):
        if not self.available: raise AIUnavailable("OPENAI_API_KEY is not configured")
        if self._client is None:
            from openai import OpenAI
            self._client=OpenAI(api_key=self.api_key)
        return self._client

    def json_completion(self, system: str, prompt: str, schema: Type[T], retries: int=1) -> T:
        last=None
        for _ in range(retries+1):
            try:
                client=self._client_obj()
                r=client.chat.completions.create(model=self.model,
                    messages=[{"role":"system","content":system},{"role":"user","content":prompt}],
                    response_format={"type":"json_object"}, temperature=0.2, max_tokens=settings.max_tokens)
                raw=r.choices[0].message.content or "{}"
                return schema.model_validate(json.loads(raw))
            except Exception as e:
                last=e
        raise AIUnavailable(f"AI response unavailable or invalid: {last}")

    def raw_json(self, system: str, prompt: str, retries: int=1) -> dict:
        last=None
        for _ in range(retries+1):
            try:
                client=self._client_obj()
                r=client.chat.completions.create(model=self.model,messages=[{"role":"system","content":system},{"role":"user","content":prompt}],response_format={"type":"json_object"},temperature=0.2,max_tokens=settings.max_tokens)
                return json.loads(r.choices[0].message.content or "{}")
            except Exception as e: last=e
        raise AIUnavailable(f"AI response unavailable or invalid: {last}")
