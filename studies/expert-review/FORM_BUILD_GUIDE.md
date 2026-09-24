# Two-stage form build guide

Use a form platform that supports one-way sections or page breaks. Do not place the agent recommendation on the same page as the independent choice.

For each case, create:

1. **Phase one page:** case ID, scenario statement, network/layout, initial telemetry, clearly labeled model-estimated beliefs, competing explanations, action descriptions/costs/delays, required action choice, and required confidence.
2. **Phase two page:** agent recommendation, required reasonableness rating, required advisory-safety choice, and optional preferred alternative, rationale, and missing-information fields.

Disable answer editing after advancing if the platform supports it. Randomize neither the action labels nor case IDs. The case order may be randomized per reviewer only if it is recorded. Export into `response-template.csv` column names. Keep the coordinator answer key private.

Before distribution, use the dry-run checklist and verify that the public form does not expose `synthetic_ground_truth`, `agent_prediction`, `agent_correct`, `agent_action_sequence`, or `final_posterior`.
