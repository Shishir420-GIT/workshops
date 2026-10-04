# AI → Agent: a student lab

Build a fictional campus guide: **LLM → RAG → tools → ADK agent → Streamlit**.

Start with **[AI_to_Agent_Lab.ipynb](AI_to_Agent_Lab.ipynb)**. It has explanations, executable cells, five exercises and checkpoints. Allow 60–90 minutes after the presentation, or work at your own pace. Basic Python functions, dictionaries and imports are enough.

## What runs for free?

- **Offline (default):** actual TF-IDF retrieval and Python tools; model answers and tool selection are clearly labelled scripted examples. No API key, model download or cloud project.
- **Live:** Gemini generation and a real Google ADK agent choosing between two tools. Requires internet, an API key and model access/quota. Hosting and model inference have separate costs.
- Optional neural embedding experiment: another API call, off by default.

This lab's local retrieval uses **lexical TF-IDF vectors**, not neural semantic embeddings. The in-memory index teaches vector search without a database service. `events.json` is a fixture standing in for a current campus API. All event data is fictional.

## 1. Get the repository

If your instructor has published it, clone the URL they give you:

```sh
git clone YOUR_INSTRUCTORS_REPOSITORY_URL ai-to-agent-lab
cd ai-to-agent-lab
```

Replace the uppercase placeholder; it is not a real URL. Alternatively, extract the source ZIP and open its `ai-to-agent-lab` folder. If you received the Git bundle, you can clone it without GitHub:

```sh
git clone AI_to_Agent_Lab.bundle ai-to-agent-lab
cd ai-to-agent-lab
```

## 2. Create an environment

Use **Python 3.12** (the tested version). Do not paste your API key into the terminal or notebook.

macOS/Linux:
```sh
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt and `.venv\Scripts\activate.bat`, or invoke `.venv\Scripts\python.exe` directly. Then:

```sh
python -m pip install --upgrade pip
python -m pip install -r requirements-lab.txt
python -m jupyter lab AI_to_Agent_Lab.ipynb
```

Run Jupyter **from this repository folder**. Select the Python kernel from this environment. The setup cell checks the folder. Run cells in order with Shift+Enter. `LIVE = False` means the whole notebook can run without a key.

## 3. Optional: use real Gemini and ADK calls

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Copy `.env.example` to `.env` using your editor/file manager. Put your key in `.env`; this file is ignored by Git.
3. Change `LIVE = True` in the notebook's setup cell and rerun it. If no key is configured, a hidden prompt asks for one.
4. The default is `gemini-3.1-flash-lite`. If your account cannot access it, choose an available function-calling Gemini model and check its pricing.

Do not assume a free API quota will be available to every account. Rate limits, eligibility and models can change. Live output varies; inspect the tool trace rather than checking for an exact sentence.

## 4. Run the finished application

In a separate terminal with the environment activated:
```sh
python -m streamlit run app.py
```

Open the localhost address Streamlit prints. Choose a stage, ask the sample question, change the venue and try an unknown event. Offline is the default. Live mode accepts your key in the sidebar or uses a configured server key. Each question starts a fresh session; it is intentionally a single-question lab, not persistent chat.

To deploy, follow **[DEPLOY.md](DEPLOY.md)**. No GCP account is needed for Streamlit Community Cloud. That service deploys from GitHub; this delivered repository has not been published or deployed for you.

## Lab route

| Stage | What changes | Inspect |
|---|---|---|
| LLM only | Prompt → generated response | Claims with no supplied evidence |
| RAG | Retrieve passages → prompt → response | Source IDs, scores and the actual prompt |
| Tool + fixed workflow | Python explicitly reads today's notice | Function input and returned dictionary |
| ADK agent | Model chooses read-only tools in a loop | Tool calls, arguments and results |
| Streamlit | The same functions behind a UI | Change the venue and compare stages |

## Project map

```text
AI_to_Agent_Lab.ipynb      guided notebook
app.py                    deployable Streamlit app
campus_lab/knowledge.py    local retrieval, prompt assembly, event tool
campus_lab/ai.py           Gemini generation and optional embeddings
campus_lab/agent.py        ADK agent, tools, isolated runner and event trace
campus_lab/walkthrough.py  explicitly scripted offline examples
data/                     fictional handbook chunks and event notice
tests/                    retrieval, tools, ADK loop and UI checks
SOLUTIONS.md              exercise hints and answers
DEPLOY.md                 Streamlit Community Cloud instructions
INSTRUCTOR.md             preparation, pacing and verification boundaries
```

## Check your work

```sh
python -m pytest -q
```

Tests do not call the network. The ADK loop test uses a deterministic fake model while executing the real ADK runner and Python tools. This tests wiring, not Gemini's intelligence or account access. See `INSTRUCTOR.md` for the actual validation record.

## Common problems

- **Wrong kernel / missing module:** stop Jupyter, activate `.venv`, start it using `python -m jupyter lab`.
- **Notebook folder error:** launch from the directory containing `campus_lab` and `app.py`.
- **429 / quota:** wait, check quota or use offline mode; repeatedly retrying will not add quota.
- **Model unavailable / auth error:** check model access and the key. Do not share raw credentials while asking for help.
- **No relevant retrieval result:** TF-IDF matches words, so synonyms can fail. Try clearer terms and compare the optional semantic experiment.
- **Agent missing a tool call:** examine instructions and tool descriptions. Prompting does not guarantee behavior.
- **Function edits not appearing:** restart the notebook kernel and run setup again; rerun Streamlit after saving.

Official references are in the notebook and deployment guide. Dependencies are pinned to the versions tested during preparation on 30 September 2026.
