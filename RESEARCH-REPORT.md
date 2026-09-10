# Adversarial Research: "Sequential Investigation Under Uncertainty" Flagship Project

## Context

Goal: a flagship resume project — a systems-engineering-heavy application where AI is one component, centered on **sequential investigation under uncertainty**: maintain competing hypotheses, track evidence, pick the next observation/experiment by information value vs. cost, update beliefs, repeat until a well-supported conclusion, with full auditability. The original inspiration (autonomous incident response) is off the table. The task: adversarially determine whether this idea is already established, whether it can be differentiated, which domain (or custom simulated world) is best, and whether to build it at all.

Method: four parallel adversarial research agents (~270 tool calls total) across (A) LLM-era scientific agents & benchmarks, (B) classical decision-theory/diagnosis foundations, (C) domain feasibility + commercial landscape, and (D) targeted verification of the winning domain's "empty niche" claim.

---

## Findings

### Wave 1A — LLM-era prior art

**Verdict: the loop as specified is NOT novel at any level.** Key evidence:

- **Robot Scientist Adam/Eve (King et al., Nature 2004 / Science 2009)** — matches the 10-step spec nearly verbatim, including cost/time-aware experiment selection to discriminate hypotheses. 17-year-old ancestor.
- **GDE (de Kleer & Williams, 1987)** — the exact mechanism for step 6: entropy-based measurement selection over a candidate set; cost-aware successors exist (Rodler 2017).
- **LLM-AutoSciLab (arXiv:2605.24043, 2026)** — essentially a clone: explicit competing-hypothesis set, discriminative acquisition (Disambiguate/Refine modes), hard budgets, bootstrap confidence gating, structured evidence memory, "LLM defines hypothesis space, engineered components do acquisition/fitting" — the same architectural thesis. Comes with benchmark **ActiveSciBench** (budgets B ∈ {20..100}).
- **BoxingGym (Stanford, NeurIPS 2025)** — 10 simulated probabilistic worlds; scores agents by **EIG and Expected Information Regret** (nested MC); includes "Box's Apprentice" (LLM writes PyMC model to guide experiment choice). Owns the evaluation methodology. Negative finding: explicit statistical model doesn't reliably help — an open, citable puzzle.
- **MAI-DxO / SDBench (Microsoft, 2025)** — cost-aware sequential diagnosis: differential (hypothesis set), buy-information actions with dollar costs, accuracy-vs-cost frontier. The famous one interviewers will name. Related: MediQ, AgentClinic, MedKGI (info-gain question selection + evidence tracking).
- **Others:** BED-LLM (ICLR 2026, LLM + sequential BED via EIG), POPPER (ICML 2025, sequential falsification with e-values/Type-I control — more rigorous stopping than the proposal), SIA "LLM-as-an-Investigator" (2026, hypothesis-probability updating in troubleshooting), AutoDS (NeurIPS 2025, Bayesian-surprise-driven MCTS), Kosmos/FutureHouse (long-horizon world model + claim-level provenance, commercial), Curie (rigor-engineering thesis already published), NewtonBench (ICLR 2026, probe simulated physics), DiscoveryWorld, Alchemy, SciExplorer (Phys Rev X 2026), InfoSeeker.
- **Commercial collision (worst framing):** AI-SRE products (Cleric, Traversal, Resolve.ai — a $1B-valuation category) ship hypothesis/evidence/budget/audit investigation in production. Avoid "investigate a dynamic system from telemetry" framing.

**Surviving narrow gaps (engineering, not research):**
1. Cost/feasibility as first-class pluggable action model (heterogeneous costs/latencies/feasibility + calibrated EIG-per-cost) — BoxingGym has EIG but no cost; SDBench has cost but no formal EIG.
2. Belief-state **calibration** measurement across an investigation (Brier/log scores, ablations) — nobody reports this; engages BoxingGym's negative finding.
3. **Human-approval epistemics**: approval gates that modify belief state, counterfactual replay from mid-investigation states — absent from research prototypes.
4. **Auditability as queryable data structure** (append-only evidence ledger; every posterior reconstructible; every action choice replays its scored candidate set).
5. **Domain-general reusable investigation engine** instantiated across ≥2 unrelated domains — every existing system is domain-locked. Nobody has shipped the substrate.

Recommended defensible framings: evaluate on BoxingGym/NewtonBench with published metrics; own the cost/feasibility axis; own the substrate claim (≥2 domains, same core); own human-in-the-loop epistemics; explicitly cite the prior art in README/talk track.

### Wave 1B — Classical foundations

**Verdict: "choose the next experiment to distinguish competing hypotheses under cost" is a comprehensively SOLVED classical problem** across settings: Chernoff 1959 (active sequential experiment choice, asymptotically optimal), MSPRT (1999/2000), Naghshvar–Javidi 2013 (M hypotheses, action costs), EC²/adaptive submodularity (Golovin–Krause 2010/2011 — greedy near-optimal even with non-uniform costs and correlated noise), Lindley 1956 → Chaloner–Verdinelli 1995 → Rainforth 2024 BOED with production tooling (Pyro OED, NIST optbayesexpt, BoTorch, DAD/iDAD/RL-BOED — millisecond non-myopic policies), Box–Hill 1967 model discrimination (industrialized in MBDoE flow reactors), GDE 1987 + Heckerman 1995 + **Dezide (commercial since 2001: cost+time-aware info-gathering/repair sequencing)**, Rish active probing 2003–05 (distributed-systems version), NASA Livingstone (flew 1999), ABCD-Strategy 2019 (budgeted causal design), CAASL 2024, online BED for partially observed dynamical systems (arXiv:2511.04403, Nov 2025). Robot Scientist **Adam (Nature 2004/Science 2009)** ran the exact cost-vs-information ablation the project would want as its headline (3× vs cheapest-first, 100× vs random); **Genesis (2024)** already scopes LLMs into exactly the hypothesis-generation/NL slots. LLM-hybrids already published ≥4×: Piriyakulkij & Ellis NeurIPS 2024 (LLM rules + SMC posterior + EIG selection), BED-LLM 2025 (by the BOED review authors themselves), MDA Aug 2026 (M-open + SMC + SBI + VoI), ZendoWorld 2026 (benchmark; finding: VLM agents propose near-uninformative experiments — Bayesian particle filters beat them).

**Genuinely open gaps (named by the field itself, Rainforth 2024 §5):**
1. **Open-ended/M-open hypothesis spaces** — the hypothesis must be *invented*, not just re-weighted. The real gap (MDA is attacking it — must state delta vs MDA).
2. **Model misspecification under adaptive design** — BAD provably degenerates when the model is wrong; "limited existing literature".
3. **Unstructured evidence → calibrated likelihood** — mapping logs/prose/images/human reports to likelihood ratios is NOT solved; the one place an LLM contributes something classical theory can't. Must be calibrated (reliability diagrams) with graceful degradation.
4. **Heterogeneous, partly irreversible, human-gated action spaces** — irreversibility + approval-as-an-action + non-stationary target under intervention: no clean formulation exists.
5. **A systems-investigation benchmark**: injected ground truth + unstructured telemetry + real action costs + cost-to-correct-conclusion curves does not obviously exist.

**The surviving thesis:** "Classical active hypothesis testing is optimal given a fixed hypothesis set and a known likelihood. In real investigation, neither holds: the hypothesis set is open and the evidence is unstructured. We supply exactly those two functions with an LLM, keep the classical decision-theoretic core intact, and show on benchmark X that we reach a correct conclusion at N% of the cost of both (i) greedy-EIG with a fixed hypothesis set and (ii) an unconstrained LLM agent."

**Hard requirements to survive the "LLM bolted on" criticism (need ≥2, with numbers):** open hypothesis space with measured closure property; calibrated unstructured-evidence likelihoods; beat a real classical baseline (greedy-EIG/EC²) on cost-to-confidence — "if you cannot beat greedy-EIG you built a worse 1987 system with a language interface"; formalized irreversibility/approval action model; a ground-truthed benchmark.

**Pre-interview reading list:** Rainforth 2024 §5, Naghshvar–Javidi 2013, King 2004, Golovin–Krause–Ray 2010, BED-LLM, Piriyakulkij & Ellis 2024.

### Wave 1C — Domains + commercial landscape

**Domain ranking:**
1. **Water distribution network contamination/leak investigation — 9.2/10, recommended flagship.** WNTR (EPA, pip-installable, wraps EPANET 2.2, seconds per run), BattLeDIM/L-Town benchmark (782 junctions, 2yr simulated SCADA, ground-truth leaks, economic-cost scoring), CANARY as baseline detector. Ground truth injectable by construction. Rich action space: field kit vs lab assay (cost/latency/fidelity trade), portable sensor relocation, hydrant flush (destructive!), valve isolation (risky, informative), tracer injection, complaint canvass, boil-water notice (terminal, needs human approval). Mechanistically distinct hypotheses (backflow vs injection vs main-break intrusion vs nitrification vs tank stratification vs sensor fault). Caveats: use WNTR MSX multi-species; hypotheses must be distinct generative models or it's a wrapper.
2. **Epidemiology outbreak-source investigation (Covasim) — 8.0.** Rich actions (test allocation, interviews, wastewater, serosurvey, sequencing, venue closure). Downsides: simulator built for forward projection (inversion effort), slow rollouts (need surrogates), political optics. (Downgraded further in Wave 2.)
3. **Custom simulated world — 6.8, use as calibration harness only.** Saturated: BoxingGym, CausaLab, CausalGame, MaD Physics (DeepMind 2026: cost-fidelity tiers + budget), DiscoveryWorld. Build a tiny analytic world only to prove EIG estimator calibration.
4. **Tennessee Eastman — 6.3, good SECOND domain for generality.** Faults 3/9/15 are provably indistinguishable passively → active diagnosis angle is real; but MATLAB tax (pyTEP) or Fortran build (tep2py), thin action space, 500 prior papers.
5–7. Food-safety traceback (great narrative, must build the simulator from scratch), power grid/pandapower (static sim → weak fault signatures), groundwater (slow, ugly, dominated by water networks).

**Killed:** earth observation (no tasking access, no ground truth), ecology (unknowable ground truth, eBird license), astronomy follow-up (Fink/BTSbot/TOM/GOATS incumbents — GOATS roadmap IS this system), climate (ECMWF operational targeting since 2015, national-lab compute), materials/chemistry ($1B+ funded SDL companies: Lila, Periodic, CuspAI, Orbital), biology (IterPert owns sequential perturbation design), neuroscience (Cleo/improv exist, illegible), robotics (wrong problem shape), telecom (no simulator, adjacent to incident response), supply chain (Resilinc/Interos sold), manufacturing RCA (Oden Agentic RCA, CausalPulse AAAI 2026), pharmacovigilance (Oracle/Veeva/regulated).

**Commercial:** MAI-DxO is the direct precedent to anchor against rhetorically ("the MAI-DxO pattern ported to a domain with injectable ground truth + real cost/risk model + auditable approval loop"). Kosmos/Edison doesn't do costly-action selection under budget — genuine differentiator vs them. Palantir AIP makes audit trails table-stakes enterprise-wise; PARC ACH 2.0 (Heuer's Analysis of Competing Hypotheses tool) is the 20-year-old ancestor of the hypothesis-evidence-matrix UI — cite both deliberately. Hound (GitHub) is a solo-scale project with the same belief-tracking data model in code auditing — proves buildability.

**Must-acknowledge tooling:** Pyro contrib.oed (EIG implemented), BoTorch/Ax, model-discrimination BOED (mutual information between model indicator and data — literally the "competing hypotheses" criterion, formalized), BED-LLM, ASIG (2026, amortized BED via GRPO).

**Three project-sinking risks (any domain):** (1) hypotheses not implemented as distinct generative models → EIG is theatre; (2) no dumb baselines (random/greedy-cheapest/static-placement) → numbers meaningless; (3) no closed-form-posterior validation of the EIG estimator in a toy world.

### Wave 2 — Adversarial verification of the water-domain gap

**Verdict: ORANGE — the "empty niche" claim as stated is false; a narrow YELLOW wedge survives.**

Prior art found in the water domain:
- **EPA/Sandia Water Security Toolkit (WST)** (archived 2026, BSD) — already ships sensor placement, **source inversion**, **grab-sample location selection**, hydrant flushing, booster injection, and **valve isolation** as batch optimizers. Not closed-loop, no agent, no hypothesis-class discrimination, no cost/latency budget, dead project. Must be cited and differentiated explicitly.
- **Rodriguez et al. 2021** (J. Infrastructure Systems; Purdue/Sandia/EPA) — iterative sampling to maximize expected scenario disagreement (hypothesis discrimination in all but name), MIP over precomputed scenario ensembles (up to 1.13M scenarios, P2 solved <20 min). **Does NOT model sampling cost or latency** — that's the wedge.
- **Ji et al. 2022 MGSM** (Water Resources Research) — dynamic cyclical grab-sampling, greedy entropy-bisection of posterior source region. The published adaptive baseline to beat.
- **Riano-Briceno et al. 2025** (ACS ES&T Water) — sequential adaptive sampling on the EPANET+WNTR+Chama stack.
- **AWS × KWR × Vitens × USEPA agentic PoC (June 2026)** — multi-agent LLM app demoed on contamination monitoring + isolation-action proposal, 13 tools incl. an EPANET MCP server. Demo only: no belief state, no EIG, no cost accounting, no benchmarks, no paper. Kills any "first agentic water investigator" claim; leaves "first rigorously benchmarked, information-theoretic, cost-aware one" open.
- **Syed et al. 2026 (PLOS ONE)** — agentic digital twins with cost-aware utility, human-approval gates, blockchain audit ledger — pre-empts several architectural selling points, but fully synthetic world, no EPANET, no information-gain criterion.
- The LLM-for-water cluster is heating up fast: EPANET-Agentic (Water Research 2026), LLM-EPANET, Mounce 2025, WRF Project 5349, SWAN working groups, >30% AI presentations at HIC 2026. Commercial products (TaKaDu, SUEZ Aquadvanced, Autodesk Info360) sell detection/RCA-lite; **nobody sells sequential hypothesis-class discrimination under an information budget**.

**Surviving wedge (verified):** cross-hypothesis-CLASS discrimination (contamination vs leak vs sensor fault vs backflow as distinct generative models) under a heterogeneous cost/latency/risk-differentiated action budget, benchmarked against published adaptive methods. Every found work either fixes the hypothesis class and optimizes sampling within it, or has rich actions but assumes the source is known.

**Feasibility red flags (verified):**
- RF-1 🔴 A naive Monte Carlo EIG loop is infeasible (~83 min/decision at 10k rollouts) → **precompute the scenario ensemble offline; belief = weighted distribution over enumerated scenarios** (the Rodriguez/WST architecture).
- RF-2 🔴 Pressure-driven leak sim (WNTRSimulator) and MSX water quality (EpanetSimulator) can't run in one engine → two-engine design, validate week 1.
- RF-4 🔴 **BattLeDIM contains leaks only, no contamination** → the leak arm is comparable to BattLeDIM entrants; the contamination cost metric must be invented and defended.
- RF-5 🟠 **Build on EPyT-Flow + EPyT-Control (MIT), not raw WNTR** — pre-built leak/sensor-fault/contamination/cyber events, MSX, Gymnasium envs; 2–4 weeks saved. (The KIOS/Bielefeld group is tooling this space — Artelt 2025 already does passive leak-vs-sensor-fault discrimination on L-Town.)
- RF-3 🟠 Drop nitrification (no validated potable-distribution MSX model) or model it phenomenologically.
- Licensing clean (EPA/BSD/MIT/CC-BY).

**Epidemiology runner-up re-check: ORANGE→RED, worse than water.** Sterchi et al. 2023 (Sci Rep) is exactly the active-querying source-detection loop; POMDP test allocation, entropy-driven sensing, and GNN source-detection benchmark reviews all exist; the LLM layer is also occupied (EpidemIQs, ARIES, EpiPlanAgent). Do not switch to epi.

---

## Verdict & recommendation

### Novelty status of the original idea: **RED** (essentially established)

The generic "evidence-grounded autonomous scientific investigation" system is established at every level: theory (Chernoff 1959, EC² 2010, BOED 1956–2024 — solved with optimality theorems and production tooling), full-loop systems (Robot Scientist Adam 2004 matches the 10-step spec verbatim including cost-aware experiment selection; Genesis 2024 already scopes LLMs into the hypothesis-generation slot), LLM hybrids (BED-LLM ICLR 2026, LLM-AutoSciLab 2026, Piriyakulkij & Ellis NeurIPS 2024, MDA 2026), benchmarks (BoxingGym owns EIG/EI-regret metrics; ActiveSciBench owns budgets; SDBench owns cost; ZendoWorld owns the negative finding), and products (MAI-DxO, Kosmos/Edison, Cleric/Traversal/Resolve.ai). **Do not build it as specified. The loop is table stakes; anyone presenting it as the contribution reads as unfamiliar with the field.**

### What survives: a modified project — **YELLOW** (established research problem, real engineering/product gap)

**RECOMMENDED PROJECT — "Cost-aware autonomous investigation of water-network events".**

One-line definition: an autonomous investigation system for simulated city water networks that, given an anomalous SCADA signal, maintains Bayesian beliefs over ~10⁵ precomputed fault scenarios spanning **four mechanistic hypothesis classes** (contamination source/time, pipe leak, sensor fault, backflow intrusion — each a distinct generative model), sequentially selects field actions (field-kit vs 24h lab grab samples, portable sensor relocation, hydrant flush, valve isolation, tracer injection, complaint canvass) by **expected information gain per unit cost/latency/risk**, gates irreversible actions behind human approval, converts unstructured evidence (complaint texts, operator notes — generated by the simulator) into **calibrated likelihood ratios via LLM**, and is evaluated on cost-to-correct-conclusion against published adaptive baselines.

The three differentiators that survived adversarial verification (need all three, with numbers):
1. **Cross-hypothesis-class discrimination** — all prior water work fixes the class ("it's contamination, find the source"); nobody discriminates contamination vs leak vs sensor-fault vs backflow as competing generative models.
2. **Cost/latency/risk/irreversibility as first-class terms in the acquisition function** — Rodriguez 2021 explicitly omits cost/latency; BoxingGym has EIG but no cost; SDBench has cost but no formal EIG; approval-as-an-action is unformalized anywhere.
3. **Rigorous evaluation + calibration** — beat Ji 2022 MGSM and Rodriguez-P2 reimplementations plus greedy-EIG/random/cheapest-first on 500 seeded episodes; report belief calibration (reliability diagrams, Brier); validate the EIG estimator against closed-form posteriors in a tiny analytic world. ("If you cannot beat greedy-EIG, you built a worse 1987 system with a language interface.")

LLM necessity (defensible): (a) unstructured evidence → calibrated likelihoods (the one function classical theory cannot supply); (b) hypothesis-set expansion when predictive checks fail (the M-open gap named by Rainforth §5; state delta vs MDA); (c) investigation narratives/explanations. The decision core stays classical and auditable.

**Architecture (engineering depth):** EPyT-Flow/EPyT-Control (MIT) + WNTR two-engine split (PDA leaks vs MSX quality); offline scenario-ensemble generation as a batch data-engineering job; event-driven investigation orchestrator with durable state, action queue with simulated latencies (actions resolve out-of-order); append-only evidence ledger where every posterior is reconstructible from (prior, likelihood, observation) and every action choice replays its scored candidate set; counterfactual replay from any ledger state ("what if the human had said no"); evaluation harness + episode seeding; observability (traces per investigation); web UI showing network map, plume, belief bars per hypothesis class, candidate-action table with EIG/cost scores, approval queue. Drop nitrification.

### Scoring matrix (veto criteria: Novelty<4, Evaluation<5, Action space<5, Feasibility<4 → reject)

| Criterion | Water (modified) | TEP active diagnosis | Epidemiology | Custom world (standalone) | Original generic idea |
|---|---|---|---|---|---|
| Novelty | 6 | 6 | **3 — VETO** | **3 — VETO** | **2 — VETO** |
| Problem importance | 7 | 6 | 8 | 4 | 6 |
| Investigation richness | 9 | 6 | 8 | 7 | 7 |
| Action-space richness | 9 | 5 | 8 | 7 | 6 |
| Data availability | 8 | 7 | 7 | n/a | 5 |
| Simulation quality | 9 | 6 (MATLAB tax) | 6 (slow) | 8 | 5 |
| Ground truth | 10 | 9 | 9 | 10 | 4 |
| Evaluation quality | 9 | 7 | 7 | 8 | 4 |
| Engineering depth | 9 | 7 | 8 | 6 | 7 |
| AI relevance | 7 | 6 | 7 | 6 | 5 |
| Demo quality | 9 | 5 | 8 | 6 | 5 |
| Resume value | 8 | 6 | 7 | 5 | 4 |
| Solo feasibility | 7 | 6 | 5 | 7 | 6 |
| **Overall** | **~8 (winner)** | ~6 (2nd domain) | vetoed | vetoed (harness only) | vetoed |

### Top 3 finalists
1. **Water-network investigation agent (recommended).** Closest prior: EPA WST + Rodriguez 2021 + Ji 2022 + AWS/KWR/EPA PoC + MAI-DxO (pattern). Biggest risk: EIG-loop compute (mitigated by precomputed ensembles) and the crowding clock (agentic-water is heating up; the *benchmarked cost-aware* slot is still open). Difficulty: ~3–4 months solo for MVP.
2. **TEP active fault diagnosis** (faults 3/9/15 provably indistinguishable passively → intervention required) — better as the **second domain** proving the engine generalizes than as a standalone.
3. **Epidemiology outbreak-source attribution** — rejected: Sterchi 2023 owns the loop, LLM layer occupied, slow simulator.

**Custom simulated world:** worse than a real domain as the flagship (BoxingGym/MaD Physics/CausaLab/ZendoWorld saturate it). Correct use: a tiny analytic world with closed-form posteriors as the calibration/unit-test harness — a rigor signal, not a headline.

### The 16 final questions
1. **Already established?** Yes — theory solved, loop built repeatedly since 2004, LLM hybrids published ≥4×, benchmarks and products exist.
2. **Established parts:** the loop itself; EIG selection; belief updating; hypothesis ranking; stopping rules; audit trails (EXPO/LABORS 2006); "LLM for hypothesis generation" (Genesis, Co-Scientist); "LLM + BED" (BED-LLM); cost-aware sequential diagnosis (MAI-DxO, Dezide since 2001).
3. **Genuinely differentiated parts:** cross-hypothesis-class discrimination; calibrated unstructured-evidence→likelihood channel; cost/latency/risk/irreversibility + approval-as-action in the acquisition function; queryable/replayable evidence ledger; evaluation vs published adaptive baselines with calibration reporting.
4. **Worth building?** Yes — the modified water project, framed as engineering, not research novelty.
5. **Best domain:** water distribution networks (EPyT-Flow/WNTR).
6. **Absolutely avoid:** materials/chemistry (capital-annihilated: Lila $1.3B, Periodic, CuspAI $2.6B), generic "AI scientist"/literature agents, astronomy follow-up (Fink/BTSbot/GOATS incumbents), IT/incident RCA (Cleric/Traversal/Resolve.ai), medicine (MAI-DxO).
7. **Custom sim environment vs real domain:** real domain wins; custom world only as calibration harness.
8. **Closest existing system:** to the original idea — LLM-AutoSciLab; to the recommended project — EPA WST + Rodriguez 2021 (mechanics), MAI-DxO (pattern), AWS/KWR/EPA PoC (agentic demo).
9. **Exact differences:** WST is a dead batch MIP with one hypothesis class and no cost/latency; Rodriguez has no cost/latency/agent/unstructured evidence; the PoC has no belief state, EIG, budgets, or benchmarks; MAI-DxO has no formal EIG, one domain, not public. Ours: closed-loop, four hypothesis classes as generative models, EIG-per-cost with irreversibility and approval gates, calibrated LLM evidence channel, replayable ledger, benchmarked.
10. **Genuinely strong resume project?** Yes, if the three differentiators land with numbers — it reads as "systems engineer who understands decision theory," which is rarer than "person who called an LLM."
11. **Strongest bullet:** "Built an autonomous investigation system for city-scale water networks (EPA EPANET/WNTR): Bayesian beliefs over 100K+ precomputed fault scenarios across 4 mechanistic hypothesis classes; field actions selected by expected-information-gain per dollar/hour with human-approval gates on irreversible actions; LLM converts unstructured complaint/operator text into calibrated likelihoods; beat published adaptive-sampling baselines by X% cost-to-correct-conclusion at matched accuracy over 500 seeded episodes, with full counterfactual-replayable evidence provenance."
12. **Interviewer challenges:** "Why not greedy-EIG/EC² alone — what does the LLM buy?"; "How is your EIG estimator validated/calibrated?"; "Isn't this MAI-DxO/WST?"; "What happens under model misspecification (BAD degeneracy)?"; "Myopic vs non-myopic?"; "Scenario discretization limits?" — the design above answers each; the README must cite Adam, GDE, BoxingGym, MAI-DxO, WST, Rodriguez, Ji, BED-LLM preemptively.
13. **MVP:** L-Town network, 3 hypothesis classes (contamination/leak/sensor-fault), precomputed ensemble, greedy EIG-per-cost, random + cheapest-first + Ji-style bisection baselines, 200 seeded episodes, calibration plots, ledger + simple UI.
14. **Exceptional:** beat the published methods (not just dumb baselines); reliability-diagram-backed LLM evidence channel; measured open-hypothesis-set expansion; same engine on a second domain (TEP or a BoxingGym env); counterfactual replay; public release of the benchmark harness.
15. **Would I build it?** The original as specified — no. The modified water project — yes: it's the only candidate surviving all veto criteria, and its risks are engineering risks (compute, integration), not existential ones (novelty, ground truth).
16. **If not this:** run the same engine against BoxingGym/ActiveSciBench and publish Expected-Information-Regret + calibration numbers — the "evaluate, don't assert" path; no substantially better project surfaced in ~270 tool calls of adversarial search.

---

## Key sources (selection — every claim above traces to one of the four agent reports)

Prior-art systems: [BoxingGym](https://arxiv.org/abs/2501.01540) · [MAI-DxO/SDBench](https://arxiv.org/abs/2506.22405) · [LLM-AutoSciLab](https://arxiv.org/abs/2605.24043) · [BED-LLM](https://arxiv.org/abs/2508.21184) · [POPPER](https://arxiv.org/abs/2502.09858) · [AutoDS](https://arxiv.org/abs/2507.00310) · [Kosmos](https://arxiv.org/pdf/2511.02824) · [Robot Scientist Adam](https://www.nature.com/articles/nature02236) · [The Automation of Science](https://www.science.org/doi/10.1126/science.1165620) · [Genesis](https://arxiv.org/abs/2408.10689) · [GDE](https://dekleer.org/Publications/Diagnosing%20Multiple%20Faults%20AIJ%20reprint.pdf) · [Piriyakulkij & Ellis](https://arxiv.org/html/2402.06025v5) · [ZendoWorld](https://arxiv.org/abs/2607.08233v1) · [MDA](https://arxiv.org/abs/2608.09696)

Theory: [Lindley 1956](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-27/issue-4/On-a-Measure-of-the-Information-Provided-by-an-Experiment/10.1214/aoms/1177728069.full) · [Chernoff 1959](https://link.springer.com/chapter/10.1007/978-1-4612-4380-9_26) · [Naghshvar & Javidi 2013](https://projecteuclid.org/journals/annals-of-statistics/volume-41/issue-6/Active-sequential-hypothesis-testing/10.1214/13-AOS1144.pdf) · [EC²](https://arxiv.org/pdf/1010.3091) · [Rainforth et al. 2024](https://arxiv.org/abs/2302.14545) · [Heckerman 1995 troubleshooting](https://arxiv.org/pdf/1302.3563) · [Dezide](https://www.dezide.com/technology/)

Water domain: [WNTR](https://github.com/USEPA/WNTR) · [EPyT-Flow](https://github.com/WaterFutures/EPyT-Flow) · [EPyT-Control](https://github.com/WaterFutures/EPyT-Control) · [Water Security Toolkit](https://github.com/USEPA/Water-Security-Toolkit) · [BattLeDIM](https://battledim.ucy.ac.cy/) · [Rodriguez et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC9628260) · [Ji et al. 2022](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2022WR032784) · [Riano-Briceno et al. 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11915354/) · [AWS/KWR/EPA PoC](https://www.kwrwater.nl/en/actueel/from-chatbots-to-agents-ais-next-wave-in-water/) · [Artelt et al. 2025](https://arxiv.org/abs/2505.07299) · [Chama](https://github.com/sandialabs/chama)
