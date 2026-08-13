# Incident: initial retrieval baseline below target

- Symptom: automated 50-question evaluation produced Top-3 accuracy of 20%.
- Cause: the index used document body text only; product names, process labels, applications, and device structures were not indexed consistently.
- Fix: searchable text now includes document metadata, and the baseline was re-run.
- Result after fix: Top-3 accuracy 38%, MRR 0.2919.
- Remaining issue: the dataset is a synthetic seed and needs domain review; the 80% target is not yet achieved.
- Prevention: every future retrieval change must run `scripts/evaluate_retrieval.py` and preserve the result JSON for comparison.
