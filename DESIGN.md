---
name: Water Investigation Agent
description: A municipal investigation instrument for tracing uncertain evidence and bounded recommendations.
colors:
  paper: "#f7f7f7"
  white: "#ffffff"
  ink: "#111c2f"
  reservoir-blue: "#12436c"
  reservoir-blue-deep: "#0b355b"
  reservoir-blue-soft: "#dce7ef"
  rule: "#b7c5d1"
  rule-soft: "#dbe2e8"
  muted: "#66758a"
  signal-orange: "#f05a18"
  signal-orange-deep: "#d84a0d"
  signal-orange-soft: "#fff0df"
  ready-green: "#52c84a"
  focus-orange: "#ff7a33"
typography:
  display:
    fontFamily: "Freeman, Arial Narrow, sans-serif"
    fontSize: "clamp(40px, 11vw, 58px)"
    fontWeight: 400
    lineHeight: 0.96
    letterSpacing: "0"
  headline:
    fontFamily: "Freeman, Arial Narrow, sans-serif"
    fontSize: "clamp(32px, 3vw, 52px)"
    fontWeight: 400
    lineHeight: 0.98
  title:
    fontFamily: "Freeman, Arial Narrow, sans-serif"
    fontSize: "21px"
    fontWeight: 400
    lineHeight: 1
  body:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 750
    lineHeight: 1.35
    letterSpacing: "0.06em"
rounded:
  square: "0"
  status-dot: "50%"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "18px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.signal-orange}"
    textColor: "{colors.white}"
    typography: "{typography.title}"
    rounded: "{rounded.square}"
    padding: "0 22px"
    height: "62px"
  button-primary-hover:
    backgroundColor: "{colors.signal-orange-deep}"
    textColor: "{colors.white}"
    typography: "{typography.title}"
    rounded: "{rounded.square}"
    padding: "0 22px"
    height: "62px"
  evidence-panel:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.square}"
    padding: "18px"
  evidence-tag-synthetic:
    backgroundColor: "{colors.signal-orange-soft}"
    textColor: "{colors.signal-orange-deep}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "4px 6px"
  evidence-tag-public:
    backgroundColor: "{colors.reservoir-blue-soft}"
    textColor: "{colors.reservoir-blue-deep}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "4px 6px"
---

# Design System: Water Investigation Agent

## Overview

**Creative North Star: "The Municipal Investigation Instrument"**

The visual system behaves like a working evidence board in a water-operations room: cool plotter-white surfaces, reservoir blues, graphite text, signal orange, ruled ledgers, network traces, stamped labels, and squared controls. It is dense because the reasoning trail stays visible, but hierarchy and repeated geometry keep the density legible.

The instrument presents uncertainty without theatricalizing it. Competing explanations remain visible beside the recommended observation and returned evidence. Public context, synthetic results, and operational boundaries are labeled at their point of use so visual confidence never outruns evidentiary confidence.

**Key Characteristics:**

- Flat, ruled, square-edged evidence surfaces rather than floating cards.
- Condensed display typography for headings, controls, sequence numbers, and measured values.
- Public Sans for explanatory copy, metadata, source notes, and limitations.
- Reservoir blue establishes structure; signal orange marks the action, active path, recommendation, or changed belief.
- Tabular numerals and ledger alignment make probabilities, costs, scores, seeds, and evidence easy to compare.
- One ordered investigation trail that reflows from a horizontal conveyor to a vertical ledger.

## Colors

The palette is cool, civic, and technical. White and pale gray make the board feel like plotted paper; blues carry structure and authority; orange is the scarce signal.

### Primary

- **Reservoir Blue:** Structural rules, quantitative marks, active navigation details, and the case dock.
- **Deep Reservoir Blue:** Headings, icon tiles, strong controls, and high-emphasis text.

### Secondary

- **Signal Orange:** The primary run action, active network node, recommended row, changed belief, and warnings that require attention.
- **Soft Signal Orange:** A bounded background for synthetic labels, changed evidence, and interpretation limits.

### Neutral

- **Plotter Paper:** The page ground outside white evidence surfaces.
- **Instrument White:** Panels, masthead, board, and high-contrast content fields.
- **Graphite Ink:** Main prose and the darkest footer field.
- **Muted Slate:** Explanations, metadata, secondary labels, and qualifications.
- **Rule Blue-Gray / Soft Rule:** One-pixel divisions, table rows, ledgers, and panel boundaries.

**The One Signal Rule.** Orange means action, change, recommendation, or an important boundary; do not use it as ambient decoration.

**The Evidence Boundary Rule.** Synthetic results use orange labeling, public context uses blue labeling, and operational limits are written explicitly. Never rely on color alone to communicate provenance or permission.

## Typography

**Display Font:** Freeman (with Arial Narrow and sans-serif fallback)  
**Body Font:** Public Sans (with system-ui and sans-serif fallback)  
**Numeric Treatment:** Tabular numerals wherever values are compared.

**Character:** Freeman gives the interface the compact authority of municipal signage and instrument labels. Public Sans keeps dense evidence, provenance, and limitations calm and readable.

### Hierarchy

- **Display** (400, responsive 40–58px; 50px on the wide hero, 0.96 line-height): the opening decision statement only.
- **Headline** (400, responsive 32–52px, 0.98 line-height): major method and audience sections.
- **Title** (400, commonly 18–25px): stage headings, component headings, prominent values, and controls; often uppercase for instrument labels.
- **Body** (400, 15px, 1.45 line-height): explanations and narrative copy; longer explanatory passages stay near 38–65 characters per line where layout permits.
- **Label** (typically 12px, up to 750 weight, tracked and uppercase when acting as metadata): provenance, statuses, table headers, and boundary notes.

**The Two-Voice Rule.** Freeman names, sequences, and measures; Public Sans explains, qualifies, and cites.

**The Comparable Number Rule.** Use tabular numerals for probabilities, ranks, scores, seeds, counts, and benchmark values.

## Layout

The wide investigation board is a four-stage conveyor: initial signal, competing hypotheses, action ranking, and collected evidence with updated belief. One-pixel vertical rules and aligned stage headings preserve a single left-to-right reading path. The dark case dock closes that path and hands off to evidence context and the two deeper audience branches.

The primary horizontal inset is 32px, tightening to 24px between 901px and 1300px. Spacing is compact inside evidence surfaces and expands between major sections. Ruled ledgers use repeated 12–18px internal gaps; longer sections use 32–74px sectional spacing. Cards do not float away from the grid: their borders align into the surrounding ledger.

At 900px and below, the masthead wraps, its navigation becomes horizontally scrollable, the four-stage board becomes a vertical sequence, the case dock becomes a stacked control group, evidence metrics become one column, and the Utility and Research branches stack. Wide ranking tables remain horizontally scrollable rather than compressing values beyond legibility. At 420px and below, the run controls, seed controls, statuses, and result ledgers simplify to single-column arrangements. Safe-area insets are honored, and coarse-pointer actions retain a 44px minimum target.

**The Unbroken Trail Rule.** Responsive layout may change direction, never investigation order or the proximity of a result to its evidence label.

## Elevation & Depth

The system is flat by default and uses no ambient drop shadows. Depth comes from tonal fields, dark bands, one-pixel rules, inset selected-row outlines, and the contrast between white evidence surfaces and the plotter-paper ground. The only glow-like treatment is a brief orange trace emphasis during an active synthetic run.

**The Ruled Surface Rule.** Establish hierarchy with borders, background tone, and adjacency before considering shadow.

## Shapes

Panels, controls, tags, tables, and icon tiles are square-edged. Thin blue-gray borders and full-width horizontal rules create the document-and-instrument silhouette. Circles are reserved for network nodes and small status indicators; they are data marks, not container styling. Inline icons use simple filled or stroked geometry that remains recognizable at small sizes.

## Components

### Buttons

- **Shape:** Square, compact, and mechanical with no corner radius.
- **Primary:** Signal-orange field with white Freeman text, a directional play mark, and a 62px desktop minimum height.
- **Hover / Focus:** Hover deepens the orange; keyboard focus uses a 3px focus-orange outline offset by 3px. The icon moves 3px on activation unless reduced motion is requested.
- **Secondary:** Dark-blue or outlined blue controls belong inside the case dock and review stepper. Disabled states lower contrast but preserve their label and geometry.

### Evidence Tags

- **Synthetic:** Orange text and border on soft orange, always including explicit synthetic wording.
- **Public:** Deep-blue text on soft blue, always including explicit public-context wording.
- **Operational boundary:** Written in full near the affected control or recommendation, such as “advisory only,” “requires utility approval,” or “not supported.” It is not represented by a color alone.

### Cards / Containers

- **Corner Style:** Square.
- **Background:** White for primary evidence, pale blue-gray for explanatory notes, deep blue for the dock and reproduction block.
- **Shadow Strategy:** None at rest; selected table rows use a one-pixel orange inset rule.
- **Border:** One-pixel blue-gray rules; strong section boundaries use reservoir blue.
- **Internal Padding:** Usually 12–20px, compact enough to preserve ledger alignment.

### Inputs / Fields

- **Style:** White, square, one-pixel ruled border. Seed values use large Freeman numerals with tabular alignment.
- **Focus:** The shared 3px orange focus outline remains visible. Inner native focus is suppressed only when the containing field supplies the visible focus treatment.
- **Validation / Disabled:** Native validation messages provide the seed constraint. Disabled run and step controls remain identifiable and do not imply availability.

### Navigation

The masthead combines the compact uppercase brand, small schematic icons, Freeman labels, and a visibly separated environment notice. Links turn orange on hover. On narrow screens navigation forms a full-width, horizontally scrollable ruled row with at least 44px targets.

### Investigation Conveyor

This signature component keeps all four states visible: signal, alternatives, ranked observations, and updated belief. The recommendation row says “Recommended next”; the leading belief is highlighted but alternatives remain present. During a run, the network trace advances over 650ms; after evidence arrives, the selected ranking and leading belief resolve over 560ms using a fast-settling ease. Reduced-motion mode removes both animations and substitutes a persistent orange outline.

### Ruled Ledgers

Method steps, candidate rankings, result summaries, gates, and document links share aligned columns, tabular figures, uppercase labels, and one-pixel row rules. Use a ledger when the visitor must compare evidence or follow an audit trail; do not turn comparable records into unrelated cards.

## Do's and Don'ts

### Do:

- **Do** keep competing hypotheses visible when emphasizing a recommendation or leading belief.
- **Do** attach “synthetic,” “public context,” “advisory only,” and approval-state language directly to the evidence or action it qualifies.
- **Do** use square edges, one-pixel rules, tabular numerals, and aligned rows to preserve the investigation-instrument character.
- **Do** preserve keyboard focus, polite live status announcements, semantic tables, non-color labels, reduced-motion behavior, and 44px coarse-pointer targets.
- **Do** preserve the four-stage investigation order when the layout collapses to mobile.

### Don't:

- **Don't** imply live utility connection, field validation, deployment, operational authority, or control capability.
- **Don't** merge synthetic benchmark results and public context into one unlabeled evidence class.
- **Don't** use orange for decoration or allow it to compete with the recommended action and changed evidence.
- **Don't** introduce rounded floating cards, ambient shadows, glass effects, decorative gradients outside the established case-dock field, or generic AI imagery.
- **Don't** animate for atmosphere; motion must show an active trace, returned evidence, or a direct control response.
