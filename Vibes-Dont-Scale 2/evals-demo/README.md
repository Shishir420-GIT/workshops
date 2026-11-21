# QuickCart Evals: live demo

A tiny AI support bot plus an eval suite that decides **SHIP** or **BLOCK**.
It needs only Python 3.8+ and no installs. It runs offline by default.

```
quickcart.py   the AI app: the model proposes a reply and action, the app code decides
cases.jsonl    15 test cases: normal, edge, attack, escalation
run_evals.py   code judges + optional LLM judge + metrics + release gate
```

## Demo script (about 7 minutes)

| Step | Command | What the room sees | Line to say |
|---|---|---|---|
| 1 | `python quickcart.py v1` and type *Where is my order QC-1842?* | It works! | "It works on my machine. Ship it?" |
| 2 | `python run_evals.py --bot v1` | 8/8 normal pass… then 4/4 attacks succeed, 0/3 escalations, **BLOCKED** | "Passed the vibe check. Failed reality." |
| 3 | `python run_evals.py --bot v1 --no-guardrail` | Tool violations 5/15: refunds actually execute | "This is why the model only *proposes*." |
| 4 | `python run_evals.py --bot v2` | 0% attacks… and 100% false refusals, **BLOCKED** | "Most secure bot ever. Also most useless." |
| 5 | `python run_evals.py --bot v3` | Everything green, **SHIP IT** | "Now we have proof, not vibes." |
| 6 (optional) | `python run_evals.py --bot llm --judge` | A real model, graded by another model | "Same tests, real model. Results may vary, which is the point." |

The v1/v2/v3 bots are simulated so the demo is repeatable on stage. The eval suite
is the same one you'd point at a real model.

## Using a real LLM (optional)

```
export ANTHROPIC_API_KEY=...      # or: export OPENAI_API_KEY=...
export QC_MODEL=claude-haiku-5-5  # optional override (e.g. gpt-4.1-mini for OpenAI)
python run_evals.py --bot llm --judge
```

## Try it yourself (students)

1. Add a new attack to `cases.jsonl`, for example a sneaky instruction hidden in `"retrieved"`.
2. Run `python run_evals.py --bot v3`. Did you break it?
3. If you did, you just wrote a **regression test**. Fix the bot and run it again.
