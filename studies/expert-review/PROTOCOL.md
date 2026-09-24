# Expert next-observation review protocol

**Frozen version:** 1.0 · **Protocol:** `independent-multinetwork-v1`

This study asks water-domain reviewers whether the agent's recommended next observation is a reasonable and safe advisory choice for an ambiguous synthetic distribution-system incident. It does not test diagnostic correctness, operational effectiveness, or field safety.

## Prespecified design

- **Pilot:** one qualified reviewer completes 3–5 cases to identify confusing instructions. Pilot responses are excluded from the final analysis.
- **Final sample:** 3–5 qualified reviewers, each reviewing all 30 cases independently.
- **Qualification:** professional practice or research experience in drinking-water distribution operations, water quality, hydraulic modeling, utility incident investigation, or closely related work. Record experience only as a range; do not collect employer or sensitive operational details.
- **Cases:** six cases from each of five independently seeded Net3/L-Town ensembles. Each ensemble contributes three contamination and three leak ground-truth cases. Incorrectly classified runs are sampled first to avoid presenting only easy successes.
- **Scope limitation:** no sensor-fault episode passed the already-frozen benchmark ambiguity gate. Sensor fault remains a competing explanation, but the review cannot estimate performance on sensor-fault ground truth.
- **Blinding:** reviewers must record their own next action before revealing the agent recommendation. Synthetic ground truth, final prediction, and later evidence stay in the coordinator-only answer key.
- **Primary outcome:** exact agreement between the reviewer's selected next action and the agent recommendation.
- **Secondary outcomes:** 1–5 recommendation-reasonableness rating, advisory-safety judgment (`safe`, `uncertain`, or `unsafe`), reviewer confidence, preferred alternative, missing information, and qualitative rationale.
- **Descriptive analysis:** report counts, exact-agreement proportion, mean confidence, mean and median reasonableness, safety counts and unsafe proportion, and pairwise inter-reviewer action agreement. With this small purposive sample, do not claim population generalization or statistical superiority.

## Procedure

1. Confirm eligibility, share the one-page brief, and obtain the consent recorded in `CONSENT.md`.
2. Assign a pseudonymous reviewer ID. Keep the identity mapping outside this repository.
3. For each case, show the scenario, initial telemetry, model-estimated beliefs, possible explanations, and four available observations. The beliefs must be labeled as synthetic model estimates, not calibrated field probabilities.
4. Record the phase-one action and confidence before showing the agent recommendation.
5. Reveal phase two. Record reasonableness, advisory safety, preferred alternative, rationale, and missing information.
6. Export responses using the exact columns in `response-template.csv`; one row represents one reviewer-case pair.
7. Validate and analyze the export with the documented command. Preserve raw responses separately and never commit identifiable information.

## Exclusions and deviations

- Exclude pilot responses, ineligible reviewers, duplicate reviewer-case rows, and responses missing the phase-one action.
- Retain `uncertain` safety responses and incomplete optional text fields.
- Report reviewer and case completion counts. Do not impute missing ratings.
- Log any protocol deviation in `RESULTS.md` before examining aggregate results.
- After the first qualifying final response, do not edit this protocol, the casebook, action definitions, thresholds, or analysis rules. A necessary change requires a new version and a restarted final collection.

## Interpretation boundary

Agreement means that experts found the same next observation plausible under the displayed synthetic evidence. It is not proof that the recommendation is correct, that the diagnosis is correct, or that the system is safe to deploy. All recommendations remain advisory and subject to utility procedures and professional judgment.
