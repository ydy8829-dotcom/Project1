# Incident: insufficient-evidence metadata mismatch

- Symptom: the generated answer correctly stated that exact etch rate and throughput were not provided, but the API still returned `insufficient_evidence: false` and confidence `0.732`.
- Cause: the flag was based only on retrieval scores, so related documents were treated as sufficient even when the requested numeric specification was absent.
- Fix: `answer_generator.py` now detects explicit abstention phrases and sets `insufficient_evidence: true`, limiting confidence to `0.35`.
- Verification: source compilation was attempted, but the Codex-side Windows Python session was unavailable. Re-run the FastAPI endpoint after auto-reload and confirm the corrected metadata.
