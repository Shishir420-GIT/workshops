# Secure AI for Sustainability - Cloud Run Container
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY .streamlit/ .streamlit/
COPY clean_air_agent/ clean_air_agent/
COPY app/ app/
COPY pytest.ini .

# Create non-root user for security best practice
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Cloud Run injects PORT (normally 8080). `exec` makes Streamlit the container's
# main process so startup/shutdown signals are handled correctly.
CMD ["sh", "-c", "exec streamlit run app/streamlit_app.py --server.port=\"${PORT:-8080}\" --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false"]
