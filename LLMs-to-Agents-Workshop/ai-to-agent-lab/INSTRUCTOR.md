# Instructor guide

## Before class

1. Read README and run the notebook offline once.
2. Install dependencies before the session; do not spend class time downloading them.
3. If using live mode, rehearse with your own key and available model. Check quota/pricing.
4. Publish this repository to your GitHub account and give students that real clone URL, or distribute the ZIP/bundle.
5. Keep the offline path available for students without accounts, keys or reliable internet.

The notebook is a follow-up lab for the presentation, not another 75 minutes squeezed into the talk. Use it for a separate 60–90 minute session or assign it as practice. During the talk, show just the live ADK/app section if time is short.

## Suggested pacing

| Minutes | Activity |
|---|---|
| 0–5 | Environment and mode |
| 5–13 | LLM only, tokens and sampling |
| 13–28 | Read chunks, inspect vectors, retrieve evidence, assemble the prompt |
| 28–36 | Event tool; change the venue; unknown event |
| 36–41 | Programmer-controlled workflow |
| 41–53 | ADK tool selection and trace |
| 53–61 | Add a small tool |
| 61–71 | Streamlit app and deployment |
| Remaining time | Questions and student changes |

## Teaching boundaries

- Offline mode is **not** a fake claim of running a model. It shows real local retrieval/functions and explicitly scripted model behavior.
- TF-IDF demonstrates lexical vectors; the optional Gemini embedding cell shows a neural semantic alternative.
- RAG is not always stale. Our particular handbook lacks today's event information.
- The event tool reads a fixture, not a real college API. Students can replace its implementation later.
- The fixed workflow intentionally hardcodes the hackathon lookup. The ADK agent selects tool calls using the model.
- A persona alone does not make an agent. Focus on the choose–execute–observe loop.
- The app starts a new ADK session for each submitted question. Conversation persistence is outside this introductory lab.

## Validation record — 30 September 2026

Prepared on Python 3.12.14. Direct dependencies are pinned to the installed versions.

- All 30 notebook cells executed in sequence from a fresh kernel in offline mode.
- Five automated tests passed: retrieval/source prompt, notice/override isolation, offline disclosure, real ADK runner with a fake model and real tools, and Streamlit UI interactions.
- The ADK test verifies that both tool results re-enter the model context and final text is collected. It makes no provider requests.
- Streamlit AppTest covered changing venue and an unknown event; the app was also opened in a browser for layout inspection.
- Dependency compatibility check passed.
- No live Gemini generation, semantic embedding API call, public GitHub publication or Community Cloud deployment was performed.

Rehearse those live paths before class. Instructions and tool descriptions do not guarantee that a model will select the correct tools or produce a correct answer.

## Assessment

Ask students to explain one claim and its source, show a changed tool result, distinguish a fixed workflow from an agent, and implement one function with an unknown-input case. Accept offline submissions if they identify the mode honestly. Use `SOLUTIONS.md` for discussion rather than requiring exact model wording.
