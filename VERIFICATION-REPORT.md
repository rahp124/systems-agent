# Verification Report: "Cost-Aware Autonomous Investigation of Water-Network Events"

**Purpose:** adversarial verification of the previous report's recommendation (see `RESEARCH-REPORT.md`), not an extension of it. Four independent verification agents attacked: (1) the AWS/KWR/EPA and Water Security Toolkit prior-art claims, (2) the water-domain novelty wedge, (3) whether the architecture exists under another name outside water, (4) simulator feasibility. Two agents extracted and grepped primary PDFs themselves rather than trusting summaries; one caught and corrected a tool hallucination about arXiv:2505.07299.

**Method caveat:** the session's web-search quota was exhausted mid-verification; agents substituted direct fetches of primary sources (arXiv/OpenAlex/Crossref/GitHub/OSTI APIs, full-text PDF extraction). Academic coverage is strong; commercial coverage is partial — Dezide/TEAMS internals, Vitens announcements, and several paywalled journals remain unverified. Absence-of-results from blocked search engines was NOT used as evidence of absence.

---

## 0. Corrections to the previous report — "I was wrong about X"

1. **I was wrong that WST is a batch, non-sequential tool.** The WST manual §11.3 documents an explicit iterative loop — detect → inversion → "small set of likely events?" → choose next grab samples → repeat — with a flowchart, a Bayesian formulation, a 95% confidence stopping criterion, and a worked three-cycle case study on Net3. "Closed-loop vs batch" is **retracted** as a differentiator. Automating a documented manual loop is engineering convenience, not novelty. ([WST manual, SAND2014-16973](https://www.osti.gov/servlets/purl/1150849))
2. **I was wrong that "nobody does cross-hypothesis-class discrimination" in water.** Artelt, Vrachimis, Eliades, Kuhl, Hammer & Polycarpou (2025), *"Interpretable Event Diagnosis in Water Distribution Networks"* ([arXiv:2505.07299](https://arxiv.org/abs/2505.07299)) discriminates **leaks vs hydraulic sensor faults as distinct generative models** with a per-class classifier, on L-Town, from the group that runs BattLeDIM. SICAMS ([arXiv:2512.15685](https://arxiv.org/abs/2512.15685)) classifies abrupt-leak/incipient-leak/sensor-fault. Both are **purely passive** (verified by full-text term counts: zero occurrences of information gain / sampling / budget / hypothesis / action in Artelt) — but the *discrimination* half of the claim is prior art and must be cited, not claimed.
3. **I overstated the AWS/KWR/Vitens/USEPA "PoC".** It was a demo at a Waterwise knowledge-exchange meeting (not HIC 2026), reported in one blog paragraph; the "13 tools including the EPANET MCP server" detail was an inference not in the source; no paper, no repo, no evaluation exists; the KWR EPANET MCP server itself is 7 thin tools with no agent loop, no beliefs, no costs (source code read directly). Of capabilities A–K it verifiably implements **one** (agentic orchestration); human oversight and governance are listed there as *unsolved concerns*. It is weaker as prior art than I claimed — but it was also never the four-party system I described.
4. **I was wrong to list "hypothesis-class discrimination via generative models over an ensemble, scored by EIG" as an unimplemented element in general.** It has a name — **Bayesian data-worth analysis / model-discrimination OED** — and was published in the water field's flagship journal in 2015 (Wöhling et al., *Water Resources Research*, [10.1002/2014wr016292](https://doi.org/10.1002/2014wr016292), across four competing models). The generic architecture (multi-fault belief + cost-aware sequential test selection) has shipped commercially since the 1990s: Qualtech **TEAMS/TEAMATE** (Pattipati's test-sequencing line), **Dezide** (Heckerman/SACSO line, since 2001), **GeNIe/SMILE** (VOI test ranking).
5. **I was wrong about the simulator plan.** The WNTR "two-engine split" workaround is moot: **EPyT-Flow** (MIT, KIOS/Bielefeld) runs leaks (as emitters) + PDA + water quality + MSX in one merged **EPANET-PLUS** engine, ships every needed event type (including the exact bias/drift/stuck/gaussian/percentage sensor-fault set as ~zero-cost post-processing on stored raw data), has a first-party parallel scenario runner, and bundles BattLeDIM/LeakDB/L-Town loaders with official scoring functions. WNTR should be an offline analysis sidecar at most.
6. **I was wrong that the architecture can be "precompute the ensemble once, then pure inference."** Hydrant flushes and valve closures change the hydraulics: every stored trace after the action time becomes wrong and the posterior silently corrupts. The correct architecture is **precompute the passive ensemble; lazily re-simulate the top-K posterior survivors (K≈500, ~30 s on 16 cores) with the intervention as a scheduled `SystemEvent`**; subsample K≈50 for EIG scoring of candidate interventions; prefer tracer injection (quality-only, reuses cached hydraulics) where informationally equivalent. This is a correctness requirement, not an optimization.
7. **I was wrong to treat backflow intrusion as a simple fourth hypothesis class.** EPANET cannot generate intrusion from computed negative pressure (no transient capability, no intrusion boundary condition). A naively prescribed inflow+source is **observationally degenerate with plain injection** — the EIG machinery would correctly report no action can separate them. Backflow must be redefined as a **composite hypothesis**: a hydraulic precursor (main break / pump trip) driving a low-pressure window that gates a prescribed inflow + contaminant source (~40 lines of custom `SystemEvent`; WNTR's salt-water-intrusion tutorial is the reference implementation). This must be decided before building the scenario generator.
8. **The EIG-per-cost objective must not be "invented".** Vershinin, Cohen & Gurewitz (2025), *"Active Sequential Hypothesis Testing with Non-Homogeneous Costs"* ([arXiv:2509.11632](https://arxiv.org/abs/2509.11632)) already derives the correct objective — expected information gain per **expected** cost, with the proof that per-step gain is wrong. Cite and use it.

**What the previous report got right, now verified from primary sources:** WST has zero representation of non-contamination event types (term counts over the full manual: "leak" 0, "backflow" 0, "sensor fault" 0, "information gain" 0, cost absent from the grabsample chapter — its objective is unweighted pairwise distinguishability that *ignores the posterior*); Rodriguez/SAND2017 adds probability-weighted expected disagreement but **no cost/latency**; BattLeDIM is leaks-only (CC-BY); the newest KIOS benchmark (Zenodo, 2026: 50,000 scenarios) is **single-class arsenic, passive, action-free**; EPyT-Control's advertised "event diagnosis" module **does not exist in code** (directory tree verified); no event-diagnosis "Battle" competition has ever been held; a 10⁴-scenario ensemble is a minutes-to-hours job with ~0.9 GB sensor-only storage (`frozen_sensor_config=True` — a make-or-break flag, 1,700× storage difference).

---

## 1. Novelty verification (capabilities A–K)

A: unknown event · B: competing causal hypothesis classes · C: evidence aggregation · D: sequential action selection · E: info-gain objective · F: cost/latency/risk constraints · G: physical interventions/observations · H: belief updates · I: agentic orchestration · J: human approval · K: auditable history.

**Established, with canonical owners:**
- B+C+H (passive, in water): Artelt 2025, SICAMS 2025 — leak vs sensor fault; contamination never included as a competing class; backflow appears nowhere in the literature (0 hits everywhere, including the 148k-character KIOS review).
- C+D+G+H (single class, in water): WST §11.3 loop; Ji 2022 MGSM (entropy-bisection grab sampling); Eliades & Polycarpou 2012 (decision-tree sampling policies); Mann/Laird 2011; Cholewa 2024 (iterative mobile sensor relocation on L-Town); Rasekh & Brumbelow 2014 (adaptive response with evolving source estimate).
- A+B+C+D+E+F+H+I+K (out of water): **MAI-DxO** (medicine, 9 of 11 capabilities, June 2025); ACTMED, BED-LLM, GraphDx, CuriosiTree, MedClarify (2025-26). Theory: Chernoff 1959 → Naghshvar–Javidi 2013 → Vershinin 2025 (heterogeneous costs). Products: TEAMS/TEAMATE, Dezide, GeNIe VOI.
- I (in water): EPANET-Agentic (Water Research 2026), KWR MCP demo — orchestration with zero diagnosis.

**The verified residual wedge (attacked from ~15 angles, survived):**
> Water-domain event diagnosis has bifurcated. One branch discriminates event **classes** but is purely passive; the other plans sequential **physical investigative actions** but inside a single assumed class ("a contaminant was injected; find where"). Across the 10 closest papers, the B-column and D-column are **disjoint** — nothing scores on both, and nothing exceeds 6.5/11 on A–K. No water system chooses which physical action to take next, under heterogeneous cost/latency/risk, specifically to discriminate between competing event classes. Active fault diagnosis (auxiliary-input design for model discrimination — Scott/Raimondo/Braatz/Mesbah) has **never been applied to a water network** (88 OpenAlex hits for "active fault diagnosis + water", zero on WDNs), despite the KIOS and Raimondo groups having already co-published on WDN set-based state estimation — a one-collaboration-away near-miss.

**Two architecture elements with no found implementation anywhere (small, compositional):** (i) human-approval latency and action irreversibility priced *inside* the acquisition function (precedence constraints in troubleshooting and cost-sensitive active learning are adjacent; nothing prices approval as an action); (ii) an append-only ledger whose replayed object is the **posterior** (event sourcing replays state since 2005; AgenTracer replays agent traces; nobody makes belief-reconstruction the invariant of a diagnostic orchestrator).

**One additional genuinely unoccupied axis (found during verification):** **latency-differentiated actions with delayed, out-of-order evidence returns.** A lab assay resolves in 24–48 h while field kits return in minutes and a flush destroys evidence you were about to sample; no benchmark or system — including MAI-DxO — models evidence arriving out of order while the belief state and action selection continue. This is also the most backend/distributed-systems-flavored part of the design.

**Unresolved risk to check before committing (couldn't verify from abstract):** Homaei et al. 2025, *Causal Digital Twins for Cyber-Physical Security* ([arXiv:2510.09616](https://arxiv.org/abs/2510.09616)) — if its "intervention" level is a real disambiguating actuator experiment rather than a do-calculus operator, it becomes the closest prior work. Read the full text first.

## 2. AWS/KWR/EPA system — feature table (verified)

| Capability | Verdict | Basis |
|---|---|---|
| A unknown event | PARTIAL | event type given as contamination |
| B competing hypotheses | NO EVIDENCE | nothing in any artifact |
| C evidence gathering | PARTIAL | "monitors, simulates, analyzes" |
| D sequential action selection | NO EVIDENCE | — |
| E info-gain objective | NO EVIDENCE | — |
| F cost/latency/risk | NO EVIDENCE | — |
| G physical interventions | SIMULATED PROPOSALS ONLY | "proposal of isolation actions" |
| H belief updates | NO EVIDENCE | — |
| I agentic orchestration | **YES** | 13 tools, single- and multi-agent |
| J human approval | NO — listed as an *open concern* | article text |
| K audit/provenance | NO — "data governance" an open concern | article text |

**Answer: 1 of 11 capabilities verified; 2 partial.** It is a reported demo, not a system — it proves the agentic plumbing is cheap (which pushes the contribution onto the decision-theoretic core and systems invariants), and it cannot be cited as prior art against B/D/E/F/H.

## 3. Water Security Toolkit — wrapper question

**Would our project merely be an AI wrapper around WST? No — but two claimed differentiators were WST's already** (the sequential loop; the Bayesian scenario posterior with a sensor-failure likelihood). What WST structurally cannot express, verified by exhaustive term counts over the full manual: any non-contamination hypothesis class; any sampling cost/latency/risk; any action other than grab samples *inside* the identification loop (flushing/valves exist only as separate offline response optimizations); unstructured evidence; approval gates; provenance. The correct posture: implement **WST-style Bayesian inversion + Sandia P1/P2 probability-weighted sampling as comparison baselines**, not describe them as absent. WST is archived/deprecated (June 2026), superseded by WNTR.

## 4. Ten closest papers (ranked by A–K coverage)

1. Ji et al. 2022 (WRR) — cyclical grab-sampling by posterior bisection, budget-aware, single class — **6.5/11**, the baseline to beat.
2. Artelt et al. 2025 — multi-class passive diagnosis — 4.5/11, breaks the B clause.
3. Eliades & Polycarpou 2012 — decision-tree sampling policies, single class — 6/11.
4. Rasekh & Brumbelow 2014 — adaptive contamination management, health-impact objective, single class — 6/11.
5. Mann/Wong/Laird/Hart/McKenna 2011 — grab-sample siting + MIQP inversion — 6/11.
6. Cholewa et al. 2024 — iterative mobile sensor relocation, sensitivity-driven, leaks only — 6/11.
7. SICAMS 2025 — passive 3-class classification — 3/11.
8. Eliades/Polycarpou/Charalambous 2011 — security sampling schedules — 4.5/11.
9. Sankary & Ostfeld 2019 — Bayesian mobile-sensor source localization, single class — 4.5/11.
10. EPANET-Agentic 2026 — orchestration + HITL, zero diagnosis — 2.5/11.

(Out-of-domain closest: MAI-DxO 9/11 — different domain, no formal EIG, no latency/irreversibility, not public.)

## 5. Outside water: established architecture, verified

The honest classification is: **a novel composition of an established architecture (Pattipati/TEAMS test sequencing; Heckerman/Dezide troubleshooting; Chernoff/Naghshvar–Javidi theory; MAI-DxO/ACTMED/BED-LLM LLM-era instances), applied to a domain where the passive-discrimination and single-class-active halves each exist but have never been coupled**, differentiated by: hypothesis-class breadth incl. a composite backflow model; latency/irreversibility/approval terms in the acquisition function; an LLM evidence channel with measured calibration; and posterior-reconstructible auditability. "Novel systems architecture" is **not** a defensible claim; "first coupling, in a physical-infrastructure setting, with the systems invariants nobody ships" is.

## 6. Simulator verdict

**Feasible. Stack: EPyT-Flow 0.17.x (MIT) + EPANET-PLUS + WaterBenchmarkHub; WNTR only as offline sidecar.** Verified numbers: L-Town 48 h ≈ 0.3–2 s/sim/core (derived from EPyT-Flow's own 365-day BattLeDIM re-simulation; **must be confirmed by a 1-day Phase-0 pilot**); 10⁴-scenario passive ensemble ≈ minutes-to-hours on 16 cores; sensor-only storage ≈ 90–260 KB/scenario with `frozen_sensor_config=True` over a superset of sensor locations (keeps "relocate portable sensor" as column selection); sensor-fault hypotheses are free post-processing; interventions require lazy top-K re-simulation (~30 s each); start single-species EPANET quality, defer MSX; always run PDA; handle non-converged runs explicitly or the posterior silently biases. Top risks: ensemble invalidation (HIGH — solved by hybrid design), backflow redefinition (MED), storage flag (MED), EPANET-PLUS immaturity — 9★, ~1 year old (MED — pin versions + golden-regression CI vs BattLeDIM 2019 scores), MSX cost (MED — avoid initially).

## 7. Minimal feasibility test (build this first, ~2 weeks after the 1-day Phase-0 timing pilot)

- **World:** EPANET Net3 (~97 nodes) or L-Town Area C; 48 h horizon, 15-min steps, PDA, single-species conservative contaminant.
- **Hidden state:** one scenario drawn from a 2,000-scenario ensemble, 500 per class: H1 leak (emitter at pipe p, diameter d, start t₀); H2 contamination (injection node n, start t₀, mass m); H3 sensor fault (drift/stuck/bias on sensor s from t₀ — post-processing); H4 backflow-composite (pipe-break precursor → pressure-gated inflow + source).
- **Initial observation:** 6 fixed sensors (4 pressure, 1 flow, 1 chlorine), ambiguous anomaly consistent with ≥2 classes (episode generator rejects trivially separable seeds).
- **Actions (5):** field-kit grab sample at node x (cost 1, latency 1 step, σ high); lab grab sample at node x (cost 5, latency 8 steps, σ low); relocate portable pressure sensor to node x (cost 3, latency 2 steps, then streams); hydrant flush at h ∈ {3 pre-vetted hydrants} (cost 10, irreversible, mutates hydraulics → triggers top-K re-simulation); wait one step (cost 0.5).
- **Belief:** p(sᵢ | o₁:t) ∝ p(sᵢ) · ∏ N(o; y_i, σ_channel), vectorized over the ensemble matrix; class posterior = sum over class members.
- **Acquisition:** EIG(a) = H(p) − E_o[H(p | o, a)] via the stored traces + noise model (Monte Carlo over the posterior mixture); score = EIG(a) / E[cost(a) + λ·latency(a)] (Vershinin form).
- **Stopping:** class posterior ≥ 0.9 or budget (30 units) exhausted.
- **Success criteria:** over 100 seeded episodes — (i) EIG-per-cost beats random and cheapest-first by ≥30% on cost-to-correct-class at matched accuracy; (ii) posterior calibration verified against a closed-form 3-hypothesis analytic toy world (exact Bayes vs the engine, agreement to numerical tolerance); (iii) at least one episode demonstrably requires an intervention (flush) to break a class tie (validates the active-diagnosis premise). If (iii) fails — i.e. passive sampling always suffices — the intervention layer is theater; redesign scenarios before scaling.

## 8. Kill list

| # | Threat | Severity | Solvable? |
|---|---|---|---|
| 1 | Mechanism not novel (Chernoff→MAI-DxO); claiming architecture novelty | **FATAL if claimed; LOW if reframed** | Yes — transfer framing, cite the lineage in README ¶1 |
| 2 | Passive multi-class diagnosis exists (Artelt/KIOS) | MED | Yes — cite as closest prior work; use as a baseline |
| 3 | KIOS crowding clock: they own BattLeDIM + EPyT-Flow, advertise (unshipped) event diagnosis, and could publish this coupling within ~a year | **HIGH** | Partially — build fast; release the mixed-class benchmark first; the benchmark gap was verified three independent ways |
| 4 | Ensemble invalidation on interventions (posterior silently corrupts) | HIGH (correctness) | Yes — hybrid lazy re-simulation design (§6) |
| 5 | Backflow degeneracy with injection | MED | Yes — composite pressure-gated hypothesis; decide pre-generator |
| 6 | AI not actually necessary: the decision core is classical; without the unstructured-evidence channel this is a Bayes project with an agent skin | **HIGH** | Yes — implement the complaint-text→likelihood channel with measured calibration (reliability diagrams) + LLM hypothesis-expansion; if calibration fails, publish that as a finding rather than hiding it |
| 7 | Self-graded world (designer sets scenarios and priors) | MED | Yes — held-out scenario generator, misspecification episodes (true event outside the ensemble), public harness + seeds |
| 8 | Solo scope creep (UI + orchestrator + benchmark + LLM channel + eval) | MED | Yes — MVP = 3 classes, 5 actions, no MSX, CLI-first; UI last |
| 9 | Simulator engine immaturity (EPANET-PLUS 9★) | MED | Yes — pin versions; golden-regression CI |
| 10 | Compute | LOW | Verified feasible (§6) |
| 11 | Public-data gap | LOW | Simulation-native ground truth; BattLeDIM CC-BY for the leak arm |
| 12 | "Looks like a toy" | MED | EPA-lineage simulator + literature baselines + released benchmark counteract it |

No FATAL item survives if #1 is reframed and #6 is actually built. The most likely real-world failure mode is **#3 + #8**: shipping slowly while the KIOS group closes the gap.

## 9. Resume value

As previously specified → **B (interesting research prototype)**. What moves it to **C (strong systems project)**: the hybrid simulation service (hot re-simulation, out-of-order delayed evidence, action queue with latencies), the posterior-reconstructible ledger with counterfactual replay, an evaluation harness with literature baselines, observability, and a real UI. What moves it to **D (exceptional)**: (i) beating Ji-2022-style and Sandia-P1/P2-style baselines, not just random; (ii) a reliability-diagram-backed LLM evidence channel (the one component with no prior implementation in infrastructure); (iii) releasing the mixed-class costed-action benchmark publicly (the verified three-way gap); (iv) demonstrated failure handling — misspecified episodes where the system correctly reports "no hypothesis fits" instead of confidently converging. A senior engineer's first probes will be "why an LLM?", "what breaks when the model is wrong?", and "isn't this WST/TEAMS/MAI-DxO?" — all three now have verified, citable answers.

## 10. GO/NO-GO

### **BUILD WITH MODIFICATIONS.**

**What must change (exhaustive):**
1. **Retract** three claims: closed-loop-vs-batch (WST §11.3), "nobody does cross-class discrimination" (Artelt 2025), and Bayesian-scenario-posterior-as-novel (WST, Rodriguez, data-worth analysis).
2. **Reframe the novelty claim** (see §5 wording): first *coupling* of multi-class event discrimination with cost/latency/risk-differentiated physical investigation, in a domain where the halves verifiably exist separately — plus three elements with no found implementation anywhere: approval/irreversibility priced inside the acquisition function; delayed out-of-order evidence handling; posterior-reconstructible ledger with counterfactual replay.
3. **Switch stack** to EPyT-Flow + EPANET-PLUS (pin versions; golden-regression CI); WNTR as sidecar only.
4. **Adopt the hybrid architecture**: passive precomputed ensemble (10⁴, frozen sensor config over a location superset) + lazy top-K re-simulation on interventions; episodic re-simulation, never step-wise control.
5. **Redefine backflow** as the composite pressure-gated hypothesis before writing the scenario generator; drop nitrification and MSX from the MVP.
6. **Use the Vershinin EIG-per-expected-cost objective** with latency and irreversibility terms — cite, don't rediscover.
7. **Elevate the benchmark to a first-class deliverable**: mixed-class scenario set + costed action API + leaderboard metric (verified unoccupied; also the best defense against the KIOS clock).
8. **Scope the LLM strictly** to the complaint/operator-text→calibrated-likelihood channel, hypothesis-set expansion on misfit, and narrative generation — with calibration measured and reported.
9. **Baselines**: random, cheapest-first, Ji-style bisection, Sandia P1/P2 reimplementation, Artelt-style passive classifier + fixed sampling, greedy-EIG-without-cost, LLM-only agent.
10. **Read Homaei 2025 (Causal Digital Twins) in full** before committing — the one unresolved prior-art risk.
11. **Run the Phase-0 timing pilot (1 day)** — one L-Town 48 h run, one 100-scenario parallel run, one frozen-config file size — before any architecture is fixed; all runtime figures above are derived, not measured.

**Final answers:**
1. **Final project definition:** an investigation platform for simulated water networks that couples multi-class event-hypothesis discrimination (contamination / leak / sensor fault / composite backflow, as distinct simulator configurations) with sequential physical action selection by expected-information-gain per expected cost, under latency, irreversibility, and human-approval constraints, with a calibrated LLM channel for unstructured evidence, a posterior-reconstructible evidence ledger, and a released mixed-class benchmark with literature baselines.
2. **Exact novelty claim:** the coupling (B×D+E+F+G) in water; approval/irreversibility inside the acquisition function; out-of-order delayed evidence; belief-replayable ledger. Explicitly *not*: the loop, the posterior, EIG, agentic orchestration, or multi-class passive diagnosis.
3. **Closest existing systems:** Artelt 2025 (passive multi-class, same network), WST §11.3 + Sandia P1/P2 (single-class sequential sampling), Ji 2022 (adaptive grab sampling), MAI-DxO (the pattern, in medicine), TEAMS/Dezide (the architecture, as products).
4. **Why not a reproduction:** each of the five holds at most one of {multi-class, cost/latency-aware active selection, physical irreversible actions, approval-priced acquisition, replayable posterior ledger}; none holds the conjunction; verified by full-text term counts and code inspection, not just abstracts.
5. **Simulator:** EPyT-Flow 0.17.x / EPANET-PLUS / WaterBenchmarkHub; PDA everywhere; single-species quality first.
6. **Minimal viable experiment:** §7 above (2,000-scenario, 4-class, 5-action, 100-episode test with three explicit success criteria, including the "interventions must matter" check).
7. **Evaluation strategy:** cost-to-correct-conclusion curves vs the seven baselines; class-identification accuracy + localization top-k; belief calibration (reliability diagrams, Brier) incl. misspecified episodes; EIG-estimator validation vs closed-form analytic world; ablations (no-LLM channel, no-cost-term, no-latency-term); all episodes seeded and replayable.
8. **First implementation milestone (~3 weeks):** Phase-0 pilot (day 1) → scenario generator for 3 classes + ensemble build (week 1) → vectorized posterior + EIG-per-cost + 3 dumb baselines + the 100-episode harness (weeks 2–3). The minimal feasibility test passing its three criteria is the gate for everything else — including the UI, the LLM channel, and the benchmark release.
