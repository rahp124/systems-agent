# Measurement-model source notes

**Purpose.** Primary-source specifications suitable for replacing the spike's
configured measurement noise. These are product performance limits, not
empirical distributions from the project's simulated network; do not treat a
`±` limit as a standard deviation without an explicitly chosen distribution.

## Candidate channels

| Investigation channel | Example primary source and exact specification | Model implication |
| --- | --- | --- |
| Fixed or portable pressure reading | TE Connectivity's M3200 industrial pressure transducer is available in 4, 7, 10, 14, 16, 17, 20, 25, 70, 200, 250, 300, 350, and 400 bar ranges and specifies **±0.25% FSO** pressure accuracy. [TE M3200 product specification](https://www.te.com/en/product-CAT-PTT0068.html) | For a selected full-scale range `FS`, model the instrument-limit half-width as `0.0025 × FS` in pressure units. Select `FS` for the modeled deployment; this source alone does not justify a location, installation, drift, or hydraulic-model error. |
| Flow-meter reading | Endress+Hauser's Promag W 10 is explicitly for water/wastewater and specifies maximum volume-flow error **±0.5% of reading ±1 mm/s** under its stated reference conditions; repeatability is **±0.1% of reading ±0.5 mm/s**. [Promag W 10 technical information](https://bdih-download.endress.com/file/005056A5E3831EED90DF194A33BCBE09/TI01580DEN_0222-00.pdf) | Convert the velocity term with the installed pipe area: a conservative absolute flow half-width is `0.005 × Q + A × 0.001 m/s`. Do not apply the specification below its reference conditions without a separate assumption. |
| Portable free-chlorine field measurement | Hach's **DR300/Pocket Colorimeter II** free-chlorine LR DPD method covers **0.02–2.0 mg/L Cl₂**. In ideal laboratory conditions, its method performance is **1.00 ± 0.05 mg/L Cl₂ (95% confidence interval)**. Hach explicitly cautions that users can obtain different results under different test conditions. [Hach Method 8021](https://cdn.hach.com/7FYZVWYB/at/ht435wq94g5x48wsn69t5scp/DOC3165301486.pdf) | At 1.00 mg/L, use a field-instrument normal approximation only if explicitly chosen: `sigma = 0.05 / 1.96 = 0.0255 mg/L`. Treat that as an ideal-condition lower bound, not a site-wide error rate. The 0.02 mg/L lower range supports a censored/below-range observation category. |
| Lab free-chlorine assay | Hach's **5.00 mg/L free-chlorine DPD Method 10102** reports ideal-condition spectrophotometer performance: at a **2.68 mg/L Cl₂** standard, the **95% confidence interval is 2.63–2.73 mg/L Cl₂**; method sensitivity is **0.03 mg/L Cl₂**. Hach again cautions that users can get different results under different conditions. [Hach Method 10102](https://cdn.hach.com/7FYZVWYB/as/fh36mxswggvmk9sg3h4qbt6g/Chlorine_Free_DPD_method_10102_16_mm_vials_DOC3165301553) | Preserve the published 95% interval. If a normal approximation is explicitly adopted, `sigma = 0.05 / 1.96 = 0.0255 mg/L` at 2.68 mg/L. Do not represent the 0.03 mg/L sensitivity as a standard deviation. |

## Implementation guardrails

- Parameterize each channel by a named instrument and deployment range; do not
  call these values generic "water sensor noise."
- Keep **instrument error**, **sampling/handling error**, and **simulator/model
  discrepancy** as separate terms. The sources above quantify only instrument/
  method performance, not transport or sampling delay.
- Preserve a seeded measurement draw and its parameters in every episode trace.
  For bounded `±` specifications, a truncated distribution or interval likelihood
  is more faithful than silently interpreting the bound as one standard deviation.
- The portable field result and the lab assay share chlorine chemistry; model a
  shared sample/process component if both are conditioned on the same grab
  sample, rather than treating them as independent confirmations.

## Source-selection note

The DR300 data sheet separately confirms free-chlorine DPD coverage
(0.02–2.00 mg/L or 0.1–8.0 mg/L Cl₂, depending on configuration). [Hach DR300
data sheet](https://cdn.hach.com/7FYZVWYB/at/8rqcxxm6vnxknp6ks5hc6n/DOC0525325023-DR300.pdf)
The channel-specific method sheet above is the source for the numerical
ideal-condition precision figure.
