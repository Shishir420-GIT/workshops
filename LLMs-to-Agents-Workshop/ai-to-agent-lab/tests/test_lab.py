import asyncio
from pathlib import Path
from unittest.mock import patch
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from pydantic import PrivateAttr
from campus_lab.knowledge import HandbookIndex, get_event_update, build_rag_prompt
from campus_lab.walkthrough import STAGES, offline_example
from campus_lab.agent import run_agent


def test_retrieval_and_source_ids():
    hits = HandbookIndex().search("team size students")
    assert hits[0]["id"] == "H1"
    assert HandbookIndex().search("team size")[0]["id"] == "H1"
    assert HandbookIndex().search("library books")[0]["id"] == "H4"
    assert HandbookIndex().search("zzzzzzzz") == []
    prompt = build_rag_prompt("Can we join?", hits)
    assert "[H1]" in prompt and "2 to 4" in prompt and "QUESTION:" in prompt


def test_current_notice_and_request_isolation():
    assert get_event_update(" HACKATHON ")["venue"] == "Auditorium"
    assert get_event_update("hackathon", "Lab 5")["venue"] == "Lab 5"
    assert get_event_update("hackathon")["venue"] == "Auditorium"
    assert get_event_update("unknown")["status"] == "not_found"


def test_scripted_mode_is_disclosed():
    for stage in STAGES:
        result = offline_example(stage)
        assert result["mode"] == "Offline scripted walkthrough"
    assert "No event notice found" in offline_example(STAGES[3], "Robotics gala")["answer"]


class ScriptedToolModel(BaseLlm):
    """Test double: executes real ADK tools without making Gemini requests."""
    model: str = "fake-for-tests"
    _step: int = PrivateAttr(default=0)

    async def generate_content_async(self, llm_request, stream=False):
        self._step += 1
        if self._step == 1:
            part = types.Part(function_call=types.FunctionCall(
                name="search_handbook", args={"query": "team size students"}, id="call1"))
        elif self._step == 2:
            part = types.Part(function_call=types.FunctionCall(
                name="latest_event", args={"event": "hackathon"}, id="call2"))
        else:
            results = [part.function_response for content in llm_request.contents
                       for part in content.parts or [] if part.function_response]
            assert any(r.name == "search_handbook" for r in results)
            assert any(r.name == "latest_event" and r.response["venue"] == "Lab 5" for r in results)
            part = types.Part(text="Test answer grounded in [H1] and the Lab 5 notice.")
        yield LlmResponse(content=types.Content(role="model", parts=[part]))


def test_real_adk_loop_with_fake_model():
    with patch("campus_lab.agent.Gemini", return_value=ScriptedToolModel()):
        result = asyncio.run(run_agent("Can three students join and where?", "dummy-test-key", venue_override="Lab 5"))
    calls = [e["name"] for e in result["trace"] if e["type"] == "tool_call"]
    assert calls == ["search_handbook", "latest_event"]
    assert "Lab 5" in result["answer"]
    assert len([e for e in result["trace"] if e["type"] == "tool_result"]) == 2


def test_streamlit_offline_flow():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    assert not app.exception
    app.selectbox[0].select(STAGES[3]).run()
    app.selectbox[1].select("Lab 5").run()
    app.button[0].click().run()
    assert not app.exception
    assert any("Lab 5" in x.value for x in app.markdown)
    app.text_area[0].set_value("Where is the Robotics gala?").run()
    app.button[0].click().run()
    assert any("No event notice found" in x.value for x in app.markdown)
    assert not app.exception
