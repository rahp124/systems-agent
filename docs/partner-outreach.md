# Partner outreach package

## Target profile

Prioritize organizations that can support a narrow, de-identified offline replay before any live integration:

1. University water-systems labs with EPANET, WNTR, hydraulic-modeling, water-quality, or utility-data research.
2. Municipal or regional utilities with an engineering, innovation, asset-management, or SCADA analytics contact.
3. Water research institutes, municipal innovation offices, and nonprofit technical-assistance groups.
4. Researchers or teams maintaining water-network simulation and benchmarking tools.

The first conversation is a fit check, not a data request. Ask whether the organization has resolved incident records and a process for approving de-identified historical exports.

## Outreach email

**Subject:** Read-only offline replay pilot for water-network investigations

Hello [Name],

I am building the Water Investigation Agent, a read-only decision-support agent for investigating suspected water-distribution events. It maintains competing explanations and recommends the next investigative observation while recording an auditable rationale.

I am looking for a small collaborator to evaluate it against de-identified historical telemetry and resolved investigation records. The first phase is strictly offline replay: no live SCADA connection, no control capability, and no change to operating procedures.

The requested scope is modest: an approved de-identified telemetry export and, where available, resolved incident, laboratory, maintenance, or operator-review outcomes. In return, I provide a reproducible replay analysis, advisory audit records, data-quality findings, and a review of agreement and failure cases. Your organization retains data ownership and controls sharing, retention, and deletion terms.

The attached pilot brief explains scope, safeguards, requested fields, and go/no-go gates. Would a 30-minute conversation with the appropriate engineering, operations, research, or data-governance contact be useful?

Thank you,

[Name]
[Role / affiliation]
[Repository link]

## Scoping-call agenda

1. Confirm the organization’s investigation workflow and the narrow use case.
2. Identify available telemetry, ticket, laboratory, maintenance, and sensor-metadata sources.
3. Confirm privacy, security, retention, and approval constraints.
4. Agree whether an offline replay is feasible and name the data/operational owners.
5. Define a preliminary success question and next decision point.

## Qualification checklist

Proceed only when all answers are affirmative:

- A named operational or research owner is interested in the use case.
- Historical telemetry can be exported through an approved process.
- At least some records have a resolved outcome or operator disposition.
- The organization can remove or protect sensitive fields before transfer.
- Offline replay can remain isolated from operational technology.

If any answer is negative, offer the public synthetic demonstration instead of requesting data.

## Attachments

- [Utility offline replay pilot brief](utility-pilot-brief.md)
- [Operational readiness package](operational-readiness.md)
- [De-identified CSV and review examples](examples/)
