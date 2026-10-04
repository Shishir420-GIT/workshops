"""Live Gemini calls. Credentials stay on the server and are passed per request."""
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.1-flash-lite"


def make_client(api_key: str) -> genai.Client:
    if not api_key or api_key == "replace_with_your_key":
        raise ValueError("Set a Gemini API key before enabling live mode.")
    return genai.Client(api_key=api_key, vertexai=False,
                        http_options=types.HttpOptions(timeout=45000))


def generate(prompt: str, api_key: str, model: str = DEFAULT_MODEL,
             temperature: float = 0.2) -> str:
    with make_client(api_key) as client:
        response = client.models.generate_content(
            model=model, contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature,
                                                max_output_tokens=1200),
        )
        return response.text or "No text returned. Inspect model access or safety settings."


def semantic_vectors(texts: list[str], api_key: str,
                     task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Optional paid/quota-limited semantic embedding experiment."""
    with make_client(api_key) as client:
        result = client.models.embed_content(
            model="gemini-embedding-001", contents=texts,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        return [embedding.values for embedding in result.embeddings]
