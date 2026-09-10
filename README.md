# Water investigation feasibility spike

This is intentionally throwaway code for validating a sequential-investigation loop before product work begins.

```bash
.venv/bin/python -m pytest
.venv/bin/python -m water_investigation.demo --seed 7
.venv/bin/python -m water_investigation.probe --network net3
```

The demo uses an analytic categorical world as an exact Bayes/EIG oracle. The probe runs the real EPyT-Flow integration separately and writes measured findings to `artifacts/`. It does not claim simulator likelihoods until the three event classes produce a coherent shared observation interface.

