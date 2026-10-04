"""Run: python -m streamlit run app.py"""
import asyncio
import json
import os
import streamlit as st
from dotenv import load_dotenv
from campus_lab.ai import DEFAULT_MODEL, generate
from campus_lab.agent import run_agent
from campus_lab.knowledge import HandbookIndex, build_rag_prompt, get_event_update
from campus_lab.walkthrough import STAGES, SAMPLE_QUESTION, offline_example

load_dotenv()
st.set_page_config(page_title="Campus guide · AI to agent", page_icon="🎓", layout="wide")
st.title("AI → evidence → tools → agent")
st.write("Follow one campus question as the system gains new capabilities.")

with st.sidebar:
    st.header("Lab controls")
    live = st.toggle("Use live Gemini / ADK", value=False)
    stage = st.selectbox("Stage", STAGES)
    model = st.text_input("Gemini model", DEFAULT_MODEL)
    # A per-user key is never put in os.environ or cached in a shared resource.
    supplied_key = st.text_input("Your API key (optional)", type="password")
    try:
        hosted_key = st.secrets.get("GOOGLE_API_KEY", "")
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        hosted_key = ""
    api_key = supplied_key or hosted_key or os.getenv("GOOGLE_API_KEY", "")
    venue = st.selectbox("Simulate today's venue", ["From events.json", "Lab 5", "Innovation Centre"])
    override = None if venue == "From events.json" else venue
    st.caption("Venue changes affect only your request. All campus data is fictional.")
    if live:
        st.caption("Model calls use API quota and may cost money. Each question starts a fresh session.")
    else:
        st.info("Offline mode uses scripted examples and real local retrieval. It is not an AI agent.")

st.graphviz_chart('digraph { rankdir=LR; node [shape=box, style=rounded]; "Question" -> "LLM"; "Handbook retrieval" -> "Context" -> "LLM"; "LLM" -> "Event tool" [dir=both]; "LLM" -> "Answer"; }')
question = st.text_area("Student question", SAMPLE_QUESTION, height=100, max_chars=1200)
st.caption("Try an eligibility question, change the venue, or ask about an unknown event.")
if st.button("Run this stage", type="primary"):
    st.session_state.pop("result", None)
    if not question.strip():
        st.warning("Enter a question first.")
    elif live and not api_key:
        st.warning("Add a Gemini API key or switch off live mode.")
    else:
        try:
            with st.spinner("Running…"):
                if not live:
                    result = offline_example(stage, question, override)
                elif stage == STAGES[0]:
                    result = {"answer": generate(question, api_key, model), "trace": [], "mode": "Live LLM only"}
                elif stage == STAGES[1]:
                    hits = HandbookIndex().search(question)
                    prompt = build_rag_prompt(question, hits)
                    result = {"answer": generate(prompt, api_key, model),
                              "trace": [{"type": "retrieved", "passages": hits}, {"type": "prompt", "text": prompt}],
                              "mode": "Live RAG"}
                elif stage == STAGES[2]:
                    # The programmer picks the event here; the LLM does not select a tool.
                    hits = HandbookIndex().search(question)
                    notice = get_event_update("hackathon", override)
                    prompt = build_rag_prompt(question, hits) + "\nNotice for hackathon ONLY:\n" + json.dumps(notice)
                    prompt += "\nDo not apply this notice to other events."
                    result = {"answer": generate(prompt, api_key, model),
                              "trace": [{"type": "fixed_lookup", "event": "hackathon", "result": notice}],
                              "mode": "Live fixed workflow (programmer-selected lookup)"}
                else:
                    result = asyncio.run(run_agent(question, api_key, model, override))
            st.session_state.result = {**result, "question": question, "stage": stage}
        except Exception:
            # Raw provider errors can include request details; don't expose them to visitors.
            st.error("The live request failed. Check your model name, API key, quota and connection; "
                     "then retry or use offline mode. The request may also have reached its time/tool limit.")

if "result" in st.session_state:
    result = st.session_state.result
    st.subheader("Result")
    st.caption(f'{result["mode"]} · {result["stage"]} · Last submitted question: {result["question"]}')
    st.markdown(result["answer"])
    with st.expander("Inspect evidence and tool events", expanded=True):
        if result["trace"]:
            for event in result["trace"]:
                st.json(event)
        else:
            st.write("No retrieval or tool events in this stage.")
    st.caption("Check the evidence yourself. Model outputs and citations can still be wrong.")
