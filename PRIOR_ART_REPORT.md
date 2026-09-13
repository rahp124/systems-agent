# Prior art record

## Conclusion

Sequential hypothesis testing, Bayesian belief updates, expected information gain, and cost-aware experiment selection are established methods. The Water Investigation Agent does not claim to invent them. Its engineering focus is an auditable application of those methods to competing water-distribution event classes, heterogeneous evidence, action cost and latency, and operator-governed response.

## Relevant lineage

- Classical active sequential hypothesis testing and Bayesian experimental design: Chernoff, Lindley, Naghshvar–Javidi, EC²/adaptive submodularity, and model-discrimination BOED.
- Diagnostic action sequencing: GDE, Heckerman troubleshooting, and Dezide.
- Sequential scientific/diagnostic agents: Robot Scientist Adam, BoxingGym, MAI-DxO/SDBench, BED-LLM, and LLM-AutoSciLab.
- Water-distribution investigation and sampling: EPA Water Security Toolkit, Rodriguez et al. (2021), Ji et al. (2022), Riano-Briceno et al. (2025), WNTR, EPyT-Flow, and EPyT-Control.

## Implications for this agent

1. Treat the analytic Bayesian implementation as a correctness oracle, not a novelty claim.
2. Compare policy behavior against meaningful baselines on identical held-out episodes.
3. Keep simulator ground truth unavailable to the agent during evaluation.
4. Preserve an auditable chain from evidence to posterior to recommended action.
5. Separate synthetic benchmark evidence from operational validation.
6. Add language-model functionality only when it contributes a measured, calibrated capability for unstructured evidence or hypothesis-set expansion.

## Current differentiation and limits

The agent currently evaluates contamination, leak, and sensor-fault hypotheses using simulator-derived traces, instrument-level assumptions, costed actions, conditional lab confirmation, and paired policy comparisons. It has not yet evaluated published water-domain adaptive-sampling baselines, operated against historian data, or supported consequential interventions. These are validation gaps, not claims of absence in prior work.

## Selected sources

- [Lindley 1956](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-27/issue-4/On-a-Measure-of-the-Information-Provided-by-an-Experiment/10.1214/aoms/1177728069.full)
- [Chernoff 1959](https://link.springer.com/chapter/10.1007/978-1-4612-4380-9_26)
- [Naghshvar & Javidi 2013](https://projecteuclid.org/journals/annals-of-statistics/volume-41/issue-6/Active-sequential-hypothesis-testing/10.1214/13-AOS1144.pdf)
- [EC²](https://arxiv.org/pdf/1010.3091)
- [Robot Scientist Adam](https://www.nature.com/articles/nature02236)
- [BoxingGym](https://arxiv.org/abs/2501.01540)
- [MAI-DxO/SDBench](https://arxiv.org/abs/2506.22405)
- [Water Security Toolkit](https://github.com/USEPA/Water-Security-Toolkit)
- [WNTR](https://github.com/USEPA/WNTR)
- [EPyT-Flow](https://github.com/WaterFutures/EPyT-Flow)
- [Rodriguez et al. 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC9628260)
- [Ji et al. 2022](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2022WR032784)
