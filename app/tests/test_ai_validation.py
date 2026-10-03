from types import SimpleNamespace
import pytest
from app.services.openai_service import OpenAIService, AIUnavailable
from app.schemas.outreach import OutreachContent


def test_demo_mode_ai_unavailable_without_key():
    ai = OpenAIService(api_key="")
    assert not ai.available
    with pytest.raises(AIUnavailable):
        ai.raw_json("x", "y", retries=0)


class BrokenCompletions:
    def create(self, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="{not valid json"))]
        )


class BrokenClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=BrokenCompletions())


def test_malformed_ai_json_is_caught_and_wrapped():
    ai = OpenAIService(api_key="fake-key")
    ai._client = BrokenClient()
    with pytest.raises(AIUnavailable, match="invalid"):
        ai.raw_json("system", "prompt", retries=0)


def test_schema_invalid_ai_response_is_caught():
    class MissingFieldsCompletions:
        def create(self, **kwargs):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content='{"subject":"Only one field"}'))]
            )

    ai = OpenAIService(api_key="fake-key")
    ai._client = SimpleNamespace(chat=SimpleNamespace(completions=MissingFieldsCompletions()))
    with pytest.raises(AIUnavailable):
        ai.json_completion("system", "prompt", OutreachContent, retries=0)
