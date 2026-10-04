# 🍃 AI Clean Air Investigator
### Secure AI for Sustainability: Workshop & Application

An educational AI-powered environmental investigation system that uses real **OpenAQ** air-quality data, **Google ADK**, **Gemini**, and **Streamlit** to investigate pollution patterns, visualize station observations, and explain possible contributing factors while enforcing strict AI security boundaries.

---

## 🏛️ Core Architectural Principles

The application maintains strict boundaries of responsibility:

| Component | Role | Architectural Rule |
| :--- | :--- | :--- |
| **OpenAQ API v3** | Environmental Data Provider | Real station measurements; bounded queries (≤5 stations, ≤48 hrs, ≤500 obs). |
| **Python** | Deterministic Computation | **Zero LLM arithmetic.** Means, medians, peaks, and % shifts calculated in pure Python/Pandas. |
| **Google ADK** | Agent Orchestration | Coordinates tools, models, instructions, and workflows using `google.adk`. |
| **Gemini** | Qualitative Interpretation | Interprets pre-calculated structured evidence; separates facts from hypotheses. |
| **Security Layer** | Multi-Tier Defense | Prompt-injection detection, secret isolation, and deterministic output validation. |
| **Streamlit** | Visual Dashboard | PM2.5 intensity map, KPI cards, interactive time-series, and AI investigation UI. |
| **Google Cloud Run** | Serverless Hosting | Containerized scale-to-zero deployment (`min-instances=0`) within free-tier limits. |

---

## 🛡️ Guardrailing a System

Security is foundational, not an afterthought:
1. **Prompt Injection Resistance (Lab 5A)**: Untrusted external data and user queries are pre-scanned. Injections like `"Ignore all previous instructions..."` are blocked before reaching the LLM.
2. **Secret Isolation (Lab 5B)**: API keys (`OPENAQ_API_KEY`, `GOOGLE_API_KEY`) reside exclusively in environment variables and are never injected into prompts, LLM context, or outputs.
3. **Deterministic Output Validation (Lab 5C)**:
   - **Station Reference Check**: Rejects fictitious stations not present in the retrieved evidence.
   - **Numeric Claim Verification**: Rejects hallucinated numbers (e.g. `"PM2.5 was 999 µg/m³"`) if they do not match computed metrics within tolerance.
   - **Causality Enforcement**: Rejects definitive causal assertions (e.g. `"Traffic caused the increase"`); requires proper hypothesis framing (`"may have contributed to"`).

---

## 📁 Project Structure

```text
C4C/
├── notebooks/
│   ├── secure_ai_sustainability.ipynb    # Master educational walkthrough (Labs 0-7)
│   └── extension.ipynb                    # Extension activity: context enrichment + Agent Runtime deployment
├── clean_air_agent/
│   ├── __init__.py                       # Package entry point (exports root_agent, runner)
│   ├── agent.py                          # Google ADK Root Agent definition
│   ├── schemas.py                        # Pydantic data models
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── openaq.py                     # OpenAQ API v3 client with bounds & offline fallback
│   │   └── analytics.py                  # Pure deterministic analytics engine
│   └── security/
│       ├── __init__.py
│       └── validators.py                 # Deterministic security & output validation
├── app/
│   └── streamlit_app.py                  # Interactive Streamlit dashboard & guardrailing sandbox
├── scripts/
│   ├── setup_venv.sh                     # macOS/Linux setup script
│   └── setup_venv_windows.ps1            # Windows PowerShell setup script
├── tests/
│   ├── test_openaq.py                    # Data retrieval & constraint tests
│   ├── test_analytics.py                 # Deterministic math tests
│   ├── test_security.py                  # Security acceptance tests
│   └── test_agent.py                     # ADK agent workflow tests
├── .env.example                          # Environment variables template
├── .gitignore                            # Secrets & cache ignore rules
├── pytest.ini                            # Pytest configuration
├── requirements.txt                      # Python dependencies
├── Dockerfile                            # Production Cloud Run container
└── README.md
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14.6)
- OpenAQ API Key ([obtain free here](https://explore.openaq.org/))
- Google Gemini API Key ([obtain free from Google AI Studio](https://aistudio.google.com/app/api-keys))

### 2. Environment Setup

#### macOS / Linux
```bash
cd /path/to/C4C
```

```bash
./scripts/setup_venv.sh
```

```bash
cp .env.example .env
```

#### Windows PowerShell
```powershell
cd C:\path\to\C4C
```

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_venv_windows.ps1
```

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your API keys:
```ini
OPENAQ_API_KEY=your_openaq_key_here
GOOGLE_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*(Note: If API keys are omitted, the application runs with high-fidelity realistic Delhi monitoring station data for offline sandbox exploration.)*

### 3. Running the Automated Tests
Run the test suite to verify data ingestion, analytics, and security validators:
```bash
pytest -v
```

### 4. Running the Streamlit Dashboard
Launch the interactive environmental investigation dashboard:
```bash
streamlit run app/streamlit_app.py --server.port 8051 --server.address 0.0.0.0
```
Open your browser at `http://localhost:8501`. Features include:
- **Filters**: Select station regions (Delhi / Anand Vihar, Pusa, Mandir Marg) or custom coordinates.
- **PM2.5 Intensity Map**: PyDeck map with scaled station markers and tooltips.
- **Key Metrics**: Real-time average, peak concentration, and diurnal trends.
- **AI Investigator**: Ask natural language questions and receive structured 4-part reports.
- **Live Guardrailing Sandbox**: Interactive panel to test prompt injection and secret defenses in real-time.

### 5. Running the ADK Agent via CLI
You can also run or debug the ADK agent directly using the ADK CLI:
```bash
adk run clean_air_agent "Investigate air quality around Anand Vihar"
```

```bash
adk web
```

### 6. Running the Educational Jupyter Notebook
Open the master educational walkthrough:
```bash
source .venv/bin/activate
```

```bash
jupyter lab notebooks/secure_ai_sustainability.ipynb
```
Follow Labs 0 through 7 cell-by-cell.

Open the extension activity after the main build:
```bash
jupyter lab notebooks/extension.ipynb
```

If VS Code shows an error such as:
```text
Running cells with 'Python 3.14.6' requires the ipykernel package.
```

it is using the global Homebrew Python instead of this project's virtual environment.
Run:
```bash
./scripts/setup_venv.sh
```

Then select the notebook kernel named:
```text
Clean Air Agent (.venv)
```

---

## ☁️ Deploying to Google Cloud Run (Lab 7)

### Deployment Architecture:
- Serverless scale-to-zero (`min-instances = 0`) to prevent unexpected idle costs.
- Containerized with non-root security standards.

### Deploy the Streamlit portal

Run this command from the repository root. The source deployment uses this
repository's `Dockerfile`, whose container command starts Streamlit at `/`.

```bash
gcloud run deploy clean-air-investigator-portal \
  --source . \
  --region us-central1 \
  --port 8080 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars GEMINI_MODEL=gemini-2.5-flash,OPENAQ_API_KEY=$OPENAQ_API_KEY,GOOGLE_API_KEY=$GOOGLE_API_KEY
```

After deployment, open the URL printed by this command. The service name must
be `clean-air-investigator-portal`; a URL for `adk-default-service-name` is the
ADK API service and is not the Streamlit portal.

### Optional: deploy the ADK API separately

This command creates an API-only service backed by Uvicorn/FastAPI. Its root
path may return `404`; use `/docs` for its API documentation. Do not use this
command to deploy the Streamlit portal.

```bash
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=us-central1 \
  clean_air_agent
```

---

## 📚 Workshop Labs Summary

- **Workshop Activity Map**: Hyper-local pollution framing, data exploration, Google AI interpretation, prototype build, extension, and demo.
- **LAB 0 — Setup**: Virtual environment, dependencies, `.env`, and minimal ADK agent check.
- **LAB 1 — Real Data**: OpenAQ API v3 ingestion, location discovery, normalization, time-series.
- **LAB 2 — Analytics**: Pure Python deterministic statistics, peak detection, rate-of-change jumps.
- **LAB 2B — Spatial Map**: Discrete station PM2.5 intensity visualization with scientific disclaimers.
- **LAB 3 — ADK Agent**: Setting up `clean_air_investigator` root agent with custom Python tools.
- **LAB 4 — AI Investigation**: Structured 4-part reporting (Observed, Pattern, Possible Factors, Further Investigation).
- **LAB 5 — Guardrailing a System**:
  - **5A**: Prompt-injection resistance & untrusted boundary.
  - **5B**: Secret isolation & credential protection.
  - **5C**: Deterministic output validation (hallucinated stations, fake numbers, unqualified causality).
- **LAB 6 — Streamlit Dashboard**: End-to-end interactive dashboard and live guardrailing sandbox.
- **LAB 7 — Google Cloud Run**: Containerization, scale-to-zero serverless deployment, and cost controls.
- **Extension Notebook**: Weather, satellite, traffic, and low-cost sensor enrichment paths, plus Google Agent Runtime deployment for the ADK agent.

## ✅ Workshop Criteria Coverage

| Criteria | Where it appears |
|---|---|
| Understand the Problem | Workshop Activity Map and hyper-local pollution primer in the main notebook |
| Explore the Data | Labs 1, 2, and 2B |
| Use Google AI | Labs 3 and 4 with Google ADK and Gemini |
| Build | Lab 6 Streamlit dashboard and agent prototype |
| Extend | `notebooks/extension.ipynb`, including Google Agent Runtime deployment |
| Demo | Participant Demo Checklist in Lab 7 |
