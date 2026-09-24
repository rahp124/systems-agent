# Dry-run checklist

Complete this with a pilot reviewer before final recruitment. Pilot responses are excluded.

- [ ] The reviewer can explain the problem and the agent's role in their own words.
- [ ] Eligibility and consent are recorded outside the repository.
- [ ] Ground truth and phase two are hidden until phase one is recorded.
- [ ] All four actions, costs, and delays are legible without source-code access.
- [ ] The reviewer understands that costs are relative and cases are synthetic.
- [ ] One response row is produced for every completed case.
- [ ] Case IDs and action values exactly match the casebook vocabulary.
- [ ] A test export passes `python -m water_investigation.expert_review analyze`.
- [ ] Completion time and confusing wording are recorded.
- [ ] Any wording change is made before final collection, followed by a version bump and regenerated casebook.
