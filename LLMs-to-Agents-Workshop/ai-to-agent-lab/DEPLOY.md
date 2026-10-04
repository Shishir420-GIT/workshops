# Deploy the Streamlit application

## Fastest path: Streamlit Community Cloud

The app runs as-is from `app.py`; no ADK Web server or GCP account is needed. Community Cloud provides free app hosting, while Gemini has separate API quotas/pricing. Deployment needs GitHub and an eligible Streamlit account.

### Instructor: publish the source once

1. Create an empty GitHub repository, for example `ai-to-agent-lab`.
2. Upload the contents of this source folder, including `campus_lab/`, `data/`, `.streamlit/config.toml` and `requirements.txt`. Keep `app.py` at the repository root.
3. Do not upload `.env`, `.streamlit/secrets.toml`, `.venv`, local outputs or keys. The included `.gitignore` handles normal Git workflows.
4. Give students the real repository URL. They can clone or fork it. No remote repository was created as part of preparing these files.

If using the supplied Git bundle, clone it first and then connect your empty GitHub repository:
```sh
git clone AI_to_Agent_Lab.bundle ai-to-agent-lab
cd ai-to-agent-lab
git remote set-url origin YOUR_NEW_GITHUB_REPOSITORY_URL
git push -u origin main
```
The uppercase value must be replaced with your actual repository URL.

### Student: deploy your copy

1. Fork the instructor's GitHub repository into your account.
2. Sign in at https://share.streamlit.io and choose **Create app**.
3. Select your repository, branch `main`, and main file **`app.py`**.
4. Under advanced settings, choose **Python 3.12**.
5. For a no-key demo, leave secrets empty. The app starts in offline mode.
6. Choose Deploy. Wait for dependency installation, then open the app URL.

To support live mode, either let each user enter a personal key in the password field, or configure a server key in the app's **Secrets** settings:

```toml
GOOGLE_API_KEY = "your_actual_key"
```

Do not put this value into the repository. A server key can consume your quota whenever a visitor enables live mode, so use personal keys for public student demos or keep a classroom app access-controlled. The app passes credentials into a request-local client; it does not change a process-wide key for other users.

## Verify the deployment

- Offline stage 1 clearly identifies its answer as a deliberately unsupported scripted example.
- Offline RAG shows real passages and source IDs.
- Changing the venue to Lab 5 changes the event evidence, without affecting other visitors.
- An unknown event returns `not_found` in the offline workflow.
- With a valid key, live ADK mode calls handbook and event tools for the combined question.
- Check the final answer against the trace, including sources and missing information.

The app is a teaching demo: one independent question per session, in-memory state, read-only tools and a small local fixture. There is no real registration, multi-user database or persistent conversation store. Public deployment and live billing have not been exercised during file preparation.

## Run without hosting

```sh
python -m streamlit run app.py
```

This requires no GitHub account. Share a screen or demonstrate locally if account setup would distract from the lab.

## Official references

- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits
