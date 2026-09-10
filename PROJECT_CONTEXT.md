# PROJECT_CONTEXT.md

## Purpose

This document is the handoff/context file for continuing this project in a Codex session.

Read this file **and `RESEARCH-REPORT.md` in full before implementing anything**. `RESEARCH-REPORT.md` is the adversarial research record and source of truth for prior-art findings. This file captures the project decisions made after that research and the intended implementation sequence.

---

# 1. Project Goal

Build a flagship portfolio project that demonstrates serious software/systems engineering where AI is **one component of a larger system**, not an LLM wrapper.

The original inspiration was an autonomous production-incident response system with the pattern:

```text
signal/event
→ collect evidence
→ form/rank hypotheses
→ decide what information/action is needed next
→ execute
→ observe result
→ update beliefs
→ repeat
→ human approval for consequential actions
→ auditable outcome
```

We deliberately do **not** want to copy incident response.

The initial alternative was a generic "Scientific Investigation Agent." Extensive adversarial research found that this broad concept is already established academically and increasingly in products/benchmarks.

Therefore, **do not build or describe this project as a novel generic AI scientist/scientific-investigation agent.**

---

# 2. Current Decision

## Status: BUILD WITH MODIFICATIONS

### Working project

**Cost-aware autonomous investigation of water-network events**

One-line formulation:

> Given an anomalous signal in a simulated city water network, maintain competing mechanistic explanations for what is happening, select the next observation/intervention based on information value versus cost/latency/risk, update beliefs from the result, and continue until reaching a defensible conclusion.

The important word is **investigation**.

The system is not merely:

- detecting anomalies,
- predicting failures,
- locating a known contamination source,
- optimizing sensor placement,
- running EPANET through an LLM,
- or generating scientific hypotheses in prose.

It must repeatedly decide:

> **Given what I currently believe and what I still do not know, what should I do next?**

---

# 3. Why the Original Idea Was Rejected

The generic loop

```text
observation
→ competing hypotheses
→ uncertainty
→ experiment selection
→ observation
→ belief update
→ repeat
```

is established.

The research report identifies prior art including classical active diagnosis / Bayesian optimal experimental design, Robot Scientist Adam/Eve, GDE, BoxingGym, MAI-DxO/SDBench, BED-LLM, LLM-AutoSciLab, POPPER, and others.

Important implication:

## DO NOT CLAIM

- that sequential investigation under uncertainty is novel;
- that expected-information-gain experiment selection is novel;
- that cost-aware diagnosis is novel;
- that Bayesian hypothesis updating is novel;
- that LLM-assisted scientific experimentation is novel;
- that this is the first autonomous water investigator;
- that an evidence/audit trail alone is novel.

These are foundations or existing ideas we are applying and engineering around.

See `RESEARCH-REPORT.md` for the actual prior-art analysis and citations.

---

# 4. Why the Water-Network Version Survived

The adversarial research found the water domain itself is active and increasingly agentic, so the project is **not an empty niche**.

Relevant existing work includes:

- EPA/Sandia Water Security Toolkit (WST)
- Rodriguez et al. 2021 adaptive/iterative sampling
- Ji et al. 2022 MGSM
- Riano-Briceno et al. 2025
- AWS × KWR × Vitens × USEPA 2026 agentic proof of concept
- EPANET/WNTR/EPyT ecosystem
- related leak/sensor-fault work

Therefore, novelty must **not** be framed as "AI for water networks."

The surviving engineering wedge is the combination of:

### A. Cross-hypothesis-class investigation

Instead of assuming:

> "There is contamination; find its source."

start with:

> "Something is wrong. What kind of event is occurring?"

Candidate mechanistic classes initially:

1. contamination
2. pipe leak
3. sensor fault

Potential fourth class later:

4. backflow intrusion

These must eventually correspond to **distinct generative models**, not just labels attached to LLM prose.

### B. Heterogeneous action economics

Candidate investigation actions should differ in dimensions such as:

- information value
- monetary/resource cost
- latency
- feasibility
- operational risk
- reversibility

Examples considered in the research:

- inspect existing sensor data
- field-kit grab sample
- delayed lab assay
- portable sensor relocation
- complaint/operator evidence
- hydrant flush
- valve isolation
- tracer injection
- public notice / other terminal safety action

Not all belong in the MVP.

### C. Rigorous evaluation and calibration

The project must demonstrate performance quantitatively against meaningful baselines.

The headline cannot be:

> "The agent gives plausible explanations."

It should eventually be something like:

> "At matched conclusion accuracy, the investigation policy reached the correct event class at X% lower cost than baseline Y across N seeded episodes."

Only use such numbers after actually measuring them.

---

# 5. Most Defensible Project Thesis

Do **not** position this as research novelty.

Position it as an engineering/evaluation thesis:

> Classical active hypothesis testing works well when the hypothesis set and observation likelihoods are known. Real investigations contain heterogeneous actions, messy evidence, operational constraints, and potentially incomplete hypothesis sets. Build an auditable investigation system that keeps the decision-theoretic core explicit while using AI only where unstructured reasoning is actually useful.

The strongest contribution is the **system and its measured behavior**, not inventing EIG or Bayesian experimental design.

---

# 6. AI / LLM Role

A critical architectural principle:

> **LLM proposes/interprets. Evidence and explicit decision machinery constrain.**

The LLM must **not** simply receive all context and decide what action to take.

Potential legitimate LLM responsibilities later:

1. Convert unstructured operator notes / complaint text into structured evidence or calibrated likelihood contributions.
2. Propose a missing hypothesis when predictive checks indicate that the current hypothesis set is inadequate (M-open behavior).
3. Explain the current investigation state and decision rationale in natural language.
4. Potentially map messy real-world evidence into structured claims.

The deterministic/probabilistic system should own:

- durable investigation state
- priors/posteriors
- scenario weights
- action costs
- action latencies
- feasibility constraints
- risk
- expected information gain
- stopping conditions
- execution
- provenance
- evaluation

Do not add an LLM until the non-LLM investigation loop works.

---

# 7. Intended Long-Term Architecture

Approximate architecture, subject to feasibility findings:

```text
              Water-network simulator
          EPyT-Flow / EPyT-Control / WNTR
                        │
                        ▼
             Hidden scenario / ground truth
                        │
                        ▼
                  Observation layer
                        │
                        ▼
               Investigation state
            ┌───────────┴───────────┐
            │                       │
       Evidence ledger        Belief state
                                    │
                                    ▼
                            Candidate actions
                                    │
                                    ▼
                         Decision / scoring layer
                         EIG + cost + latency
                         + risk + feasibility
                                    │
                                    ▼
                         Human approval gate
                         when consequential
                                    │
                                    ▼
                              Execute action
                                    │
                                    ▼
                               New evidence
                                    │
                                    ▼
                            Bayesian update
                                    │
                                    └── repeat
```

Potential later supporting systems:

- offline scenario-ensemble generation
- durable workflow orchestration
- simulated asynchronous action completion
- append-only evidence ledger
- replay from arbitrary investigation states
- observability/tracing
- evaluation harness
- web UI

Do not implement all of these up front.

---

# 8. Evidence Ledger Principle

Long term, every material belief/action should be reconstructible.

A useful target is that an investigation can answer:

> Why was hypothesis H assigned probability P at time T?

and reconstruct it from:

- prior state
- observation
- likelihood/update
- resulting posterior

Likewise:

> Why was action A selected?

should be reconstructible from the candidate action set and their scores/constraints at that moment.

Potential future feature:

> Counterfactual replay: "What would have happened if the human rejected action A?"

This is a later feature, not MVP work.

---

# 9. Simulator / Tooling Findings to Respect

The research report recommends looking first at:

- EPyT-Flow
- EPyT-Control
- WNTR
- EPANET / EPANET-MSX where needed
- L-Town / BattLeDIM where appropriate

Important caveats from the research:

1. BattLeDIM/L-Town data is leak-oriented; it does not magically provide contamination ground truth.
2. Leak hydraulics and multi-species water-quality simulation may require different simulator paths/engines. Validate this immediately rather than designing around an assumption.
3. A naive online Monte Carlo EIG implementation may be far too slow.
4. The likely scalable design is to precompute an ensemble of possible scenarios offline and maintain a weighted belief distribution over them.
5. Do not include nitrification initially; the report flagged modeling/validation concerns.
6. EPyT-Flow / EPyT-Control may save substantial implementation time relative to building directly on raw WNTR. Verify this empirically.

Do not assume the research report's implementation recommendation is infallible. The first code milestone is specifically intended to validate it.

---

# 10. THE IMMEDIATE NEXT MILESTONE

## Do not build the full product yet.

The next task is a **feasibility spike**.

Goal:

> Prove that a tiny, mathematically valid sequential investigation can be implemented in the chosen water-network environment.

### Target tiny loop

```text
hidden event
    ↓
ambiguous initial observations
    ↓
belief over 3 event classes
    ↓
3-ish candidate actions
    ↓
score/select an action
    ↓
simulator returns observation
    ↓
Bayesian update
    ↓
belief changes
    ↓
select next action
```

### Initial event classes

Start with three:

- contamination
- leak
- sensor fault

Backflow can wait.

### Requirements

The initial observations must be deliberately ambiguous enough that no single hypothesis trivially wins.

Different actions must have genuinely different expected information under the competing models.

The posterior update must be mathematically defensible.

The action-selection calculation must be testable.

---

# 11. Before Using the Water Simulator: Tiny Analytic Harness

Before trusting a simulator-derived EIG implementation, create a tiny analytic environment where the correct posterior and expected information gain can be calculated exactly or by straightforward enumeration.

Purpose:

- validate Bayesian update code
- validate entropy/information-gain code
- validate action ranking
- detect numerical mistakes
- create unit tests

This analytic world is **not the project**. It is a correctness harness.

A project-sinking failure would be an impressive UI built on incorrect EIG math.

---

# 12. Feasibility Spike Questions

The first Codex work should answer these empirically:

1. Can the recommended simulator/tooling run locally in the project environment?
2. Can we load an appropriate water network such as L-Town?
3. Can we inject/simulate a leak?
4. Can we inject/simulate contamination?
5. Can we create a sensor-fault observation model?
6. Can these scenarios expose comparable observation interfaces?
7. Can we hide scenario ground truth from the investigator while retaining it for evaluation?
8. Can we define at least three actions that produce different observation distributions under the hypotheses?
9. Can we compute/update a belief distribution after an action?
10. Can we calculate EIG correctly and cheaply enough for a toy version?
11. Do leak and contamination simulation require separate engines in practice?
12. If so, can we normalize their outputs behind one environment interface?
13. Can we seed scenarios reproducibly?
14. How long does scenario generation/simulation take?

Produce evidence for these answers; do not guess.

---

# 13. Go / No-Go Criteria for the Spike

Continue if we can demonstrate:

- ≥3 mechanistically distinct hidden event classes
- ambiguous initial evidence
- ≥3 meaningful candidate investigation actions
- different action likelihoods across hypotheses
- correct Bayesian updates
- validated EIG/action ranking
- reproducible seeded scenarios
- practical simulation/runtime path

Reconsider or redesign if:

- event classes are trivially distinguishable from passive telemetry;
- the proposed actions do not materially change uncertainty;
- simulator integration makes cross-class comparison incoherent;
- likelihoods can only be invented arbitrarily rather than derived/estimated defensibly;
- EIG computation is impractically expensive even with reasonable precomputation;
- the water-specific action space collapses into "query another sensor";
- the project becomes an LLM wrapper around EPANET.

---

# 14. Baselines

Eventually the system needs meaningful comparisons.

At minimum consider:

- random action selection
- cheapest-first
- greedy EIG
- relevant published adaptive sampling baseline(s)

The research report specifically identifies Ji-style adaptive sampling / Rodriguez-style methods as important water-domain comparisons.

Do not claim improvement until reproducing or implementing an appropriate baseline fairly.

Potential later comparisons:

- LLM-only action selector
- static sensor/sampling policy
- other classical active-diagnosis policies

---

# 15. Evaluation Metrics

Candidate metrics:

- correct event-class identification
- correct source/location where relevant
- number of actions to conclusion
- total investigation cost
- elapsed/simulated latency
- risk incurred
- cost-to-correct-conclusion
- posterior entropy / uncertainty reduction
- false-conclusion rate
- Brier score
- log score
- calibration/reliability diagrams
- robustness to noisy/missing evidence

The primary metric should eventually be something decision-relevant such as **cost-to-correct-conclusion at matched accuracy**, not merely model accuracy.

---

# 16. What Makes This Resume-Worthy

This project is worth building only if it demonstrates more than LLM integration.

Desired engineering signals:

- probabilistic reasoning
- decision theory / experimental design
- simulation
- data engineering
- backend state management
- workflow orchestration
- heterogeneous tool/action execution
- human-in-the-loop control
- reproducibility
- observability
- rigorous benchmarking
- calibrated uncertainty
- polished visualization

The intended story is:

> "I built an investigation system, established ground truth through simulation, compared its decision policy against meaningful baselines, and measured whether it reached correct conclusions more efficiently."

Not:

> "I made an AI agent that talks to EPANET."

---

# 17. Resume Claim Discipline

A future bullet might eventually resemble:

> Built an autonomous investigation system for city-scale water networks using Bayesian beliefs over precomputed fault scenarios spanning multiple mechanistic event classes; selected field actions using expected information gain under cost/latency/risk constraints, with auditable evidence provenance and human approval for consequential interventions.

Then add a measured result only after evaluation:

> Reduced cost-to-correct-conclusion by X% versus Y at matched accuracy across N seeded episodes.

Never fabricate X/Y/N.

Avoid words like "novel," "first," or "state of the art" unless later evidence genuinely supports them.

---

# 18. Important Prior Art / Interview Preparation

Before presenting this project publicly, understand and cite the relevant prior art rather than hiding it.

The research report recommends familiarity with work including:

- classical Bayesian/optimal experimental design
- active sequential hypothesis testing
- GDE / active diagnosis
- Robot Scientist Adam
- EC² / adaptive submodularity
- BoxingGym
- MAI-DxO / SDBench
- BED-LLM
- LLM-AutoSciLab
- EPA Water Security Toolkit
- Rodriguez et al. adaptive water sampling
- Ji et al. MGSM
- AWS/KWR/Vitens/USEPA agentic water-network PoC

See `RESEARCH-REPORT.md` for citations and details.

Likely interviewer questions:

- Why not greedy EIG alone?
- What does the LLM actually add?
- How do you validate the EIG estimator?
- Isn't this just WST / adaptive sampling / MAI-DxO in another domain?
- How do you handle model misspecification?
- What if the true hypothesis is not in the candidate set?
- Why myopic rather than non-myopic planning?
- How does scenario discretization affect the posterior?
- Are the likelihoods calibrated?
- Why is an intervention worth its operational risk?

The implementation should eventually provide empirical answers.

---

# 19. Scope Control

Do NOT start by adding:

- many agents
- RAG
- Kubernetes
- a graph database
- a vector database
- a complex frontend
- a workflow framework
- real cloud deployment
- multiple scientific domains
- an LLM
- a giant scenario library

unless a concrete requirement emerges.

Preferred progression:

1. analytic correctness harness
2. simulator feasibility
3. tiny investigation loop
4. scenario ensemble
5. baselines
6. evaluation
7. durable investigation state/evidence ledger
8. heterogeneous action model
9. human approval
10. LLM evidence channel
11. polished UI
12. optional second domain/generalization

---

# 20. First Codex Instruction

After reading this file and `RESEARCH-REPORT.md`, do **not** immediately implement the application.

First:

1. Inspect the repository and current environment.
2. Verify which recommended water-network libraries can be installed/run.
3. Propose the smallest feasibility spike satisfying the requirements above.
4. Identify any assumptions in this document or `RESEARCH-REPORT.md` that need empirical validation.
5. Produce a short implementation plan for the spike.
6. Only then begin the spike.
7. Keep the implementation intentionally small and instrumented.
8. Record findings, failures, runtimes, and deviations from the research assumptions.

The first success criterion is not a UI.

It is:

> **A reproducible tiny investigation where hidden ground truth exists, initial evidence is ambiguous, an information-theoretic policy chooses a meaningful next action, the simulator produces new evidence, and the posterior updates correctly.**

---

# 21. Final Current Position

**Project:** Cost-aware autonomous investigation of water-network events  
**Decision:** BUILD WITH MODIFICATIONS  
**Novelty claim:** engineering/system differentiation, NOT invention of sequential investigation  
**Primary domain:** simulated drinking-water distribution networks  
**Initial classes:** contamination / leak / sensor fault  
**Core decision machinery:** explicit Bayesian/decision-theoretic system  
**LLM:** later, narrow semantic role  
**Immediate task:** analytic correctness harness + simulator feasibility spike  
**Do not build yet:** full agent, polished UI, large architecture  
**Kill/rethink condition:** inability to construct a rigorous, nontrivial cross-hypothesis investigation environment

Read `RESEARCH-REPORT.md` for the adversarial research evidence behind these decisions.
