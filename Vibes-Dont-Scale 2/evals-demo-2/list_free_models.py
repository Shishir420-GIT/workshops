"""
List the free models OpenRouter actually has live right now.

The free-tier catalog changes week to week (new models show up, old ones
roll off, shared-pool rate limits vary by provider). Rather than hardcoding
a model name from a screenshot that will be stale in a month, ask the API:

    export OPENROUTER_API_KEY=sk-or-v1-...
    python list_free_models.py
    python list_free_models.py --probe     # also test each one with a tiny
                                            # real request and show who's
                                            # actually reachable right now
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_KEY = os.environ.get("OPENROUTER_API_KEY")


def fetch_models():
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {API_KEY}"} if API_KEY else {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def is_free(m):
    p = m.get("pricing", {})
    return m["id"].endswith(":free") and p.get("prompt") == "0" and p.get("completion") == "0"


def probe(model_id):
    body = {"model": model_id, "max_tokens": 10,
            "messages": [{"role": "user", "content": "Say OK."}]}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            json.load(r)
        return True, int((time.time() - t0) * 1000), ""
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode() or "{}").get("error", {})
        return False, int((time.time() - t0) * 1000), err.get("message", str(e))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true",
                     help="send a tiny real request to each free model to check it's reachable")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    if not API_KEY:
        print("Set OPENROUTER_API_KEY first (no card needed to list models).", file=sys.stderr)
        sys.exit(1)

    models = [m for m in fetch_models() if is_free(m)]
    models.sort(key=lambda m: m.get("created", 0), reverse=True)
    models = models[: args.limit]

    print(f"{len(models)} free models (newest first):\n")
    for m in models:
        line = f"  {m['id']:<48} {m.get('name', '')}"
        if args.probe:
            ok, ms, err = probe(m["id"])
            status = f"\033[92mOK {ms}ms\033[0m" if ok else f"\033[91m{err[:60]}\033[0m"
            line += f"  -> {status}"
        print(line)


if __name__ == "__main__":
    main()
