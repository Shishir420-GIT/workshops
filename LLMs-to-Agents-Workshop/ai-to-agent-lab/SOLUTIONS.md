# Exercise hints and answers

Try the notebook first. These are expected concepts, not exact live-model wording.

## 1. Sampling

Top-k = 2 keeps tea and coffee. Top-p = 0.85 keeps tea, coffee and water: 0.50 + 0.30 + 0.10 = 0.90. Top-p = 0.60 keeps tea and coffee (0.80). The retained probability can exceed the threshold. Sampling renormalizes the retained set before selection. Lower temperature sharpens the distribution; none of these controls supplies missing facts.

## 2. Retrieval

`team size` matches H1. `library books` should rank H4 first. The synonym-heavy query may have weak or no overlap. TF-IDF is lexical: it does not understand that “participants in a group” can mean “team members.” Neural embeddings can help, but similarity remains an imperfect retrieval signal. H1 gives the team size/year rules; no chunk establishes today's venue.

## 3. Tools

`get_event_update("hackathon", venue_override="Lab 5")` returns Lab 5 for that call. The following call without an override still returns Auditorium. Unknown names return `not_found`. A tool must not silently invent a record. In a real service, implement authentication, timeouts and validated responses at the tool boundary.

## 4. ADK tool selection

- Team size: `search_handbook` is sufficient.
- Current hackathon venue: `latest_event` is needed.
- Combined question: both are needed.
- Unknown event: a failed lookup is evidence of missing data, not permission to guess.

The trace proves which calls were made, not that the final answer is correct. The offline walkthrough always follows a fixed sequence and cannot demonstrate model-driven decisions. The live agent might make different decisions; inspect and evaluate it.

## 5. New tool

```python
def submission_deadline(event: str) -> dict:
    """Return a fictional submission deadline for a campus event."""
    deadlines = {"hackathon": "Friday, 5 PM", "robotics showcase": "Monday, noon"}
    deadline = deadlines.get(event.strip().lower())
    return {"deadline": deadline, "source": "Fictional lab schedule"} if deadline else {"status": "not_found"}
```

Add the function inside `build_agent` in `campus_lab/agent.py`, add it to `tools=[search_handbook, latest_event, submission_deadline]`, and instruct the agent to use it for deadlines. Restart/reload after editing. Ask a deadline question and verify the call and result. A docstring describes the capability; it does not implement it. Python code still matters.
