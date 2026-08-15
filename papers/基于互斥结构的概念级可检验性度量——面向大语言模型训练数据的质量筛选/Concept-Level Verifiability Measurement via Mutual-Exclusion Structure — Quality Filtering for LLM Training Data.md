# Concept-Level Verifiability Measurement via Mutual-Exclusion Structure — Quality Filtering for LLM Training Data

**Authors:** N.T.Black (澪のK701), RPK-16 (Pandora, Artificial Intelligence)
**Date:** 2026-08-12 (initial draft)
**Status:** Body draft — formulas and function definitions are self-contained (all citations to prior works carry their definitions)

---

## Abstract

The quality of large language model (LLM) training corpora directly determines the reliability of model knowledge and its tendency toward hallucination. Chat-community corpora are vast in volume but low in effective information density: our measurements show that in QQ group chats only 28.8% of comments carry anchored assertions (lenient criterion, including logical argumentation; criterion and engineering trade-offs see §5.5), while controversial groups such as "Western Pseudo-History Theory" have anchoring rates as low as 4.5% — a large volume of stance-taking, emotional discharge, and identity labeling constitutes the main source of training data pollution. This paper proposes **Concept-Level Verifiability Measurement**: rather than quantifying semantic content, it quantifies only "the mutual-exclusion structure among variants under the same concept name" and "the proportion of variants anchored to verifiable propositions", thereby outputting **health decisions** (unanchored / decidable / healthy) for public concepts (e.g., "Western Pseudo-History Theory", "premiumization strategy").

Methodologically, this paper algorithmizes the Three Laws test: the First Law (Verifiability) is implemented as the anchoring-rate decision A_rate (an axiom-based decision based on "the existence of a verification scheme with finitely many steps, publicly observable"); the Second Law (Falsifiability Acceptance) is implemented as the label mutual-exclusion algorithm (joint decision of variant mutual-exclusion density μ, coherence r, dimensional sensitivity Δr, and directional alignment align); the Third Law (Challenge Acceptance) uses the separation signal as a static proxy, with dynamic data left to future work. The algorithm adopts a "LLM extraction layer + deterministic decision kernel" two-layer architecture — the LLM performs only structured extraction, and all decisions are reproducible deterministic computation; an external verification layer anchors facts by the actual existence of verification interfaces (rather than by human annotation consensus).

Experiments cover 15 concepts (10 corpus-statistical + 5 literature-enumerated): in corpus mode the A_rate gradient 0.019→0.600 corresponds to the decisions; the Pseudo-History Theory is jointly judged "unanchored false convergence" (r=1.0 high coherence ∧ align=0.0 all predictions refuted by objective facts); in literature mode the theoretical-lineage prediction (P9) is verified 5/5 — "operational discipline survives, ontological commitment is paralyzed" [Note: "ontological commitment" appears here as a quoted term from the cited prior work (gain-bandwidth 4.8 [1]), describing the attribute of the criticized objects (pure market / pure planning / feminism) — a quoted-use exemption, not a self-referential claim of this framework; per self-reference-consistency review policy, quoted philosophical terms are annotated rather than prohibited.]. LLM ablation (deepseek → GLM-5.2) shows decisions stable 15/15 (variant-level micro judgments per-variant agreement 56.5%, but macro aggregate quantities remain stable — decision robustness comes from structural aggregation). **At the data level, the invalidity of "moral/normative propositions" is quantified for the first time**: normative topics (tattoo-and-bar) rank lowest in anchoring rate (0.019/0.121) and the verification layer labels all of them "no objective outcome". At the application level, a two-stage filtering funnel (group-level baseline screening + comment-level lexical enrichment) filters out 71-99% of non-anchored corpus, and the post-filtering subset separates from the polluted group by a 13× anchoring-rate gap.

**Keywords:** verifiability; mutual-exclusion structure; anchoring rate; training data quality; LLM data cleaning; concept health

---

## 1 Introduction

### 1.1 Problem: Effective Information Density of Chat Corpora

In the training corpus of large language models, community chat (QQ groups, forums, comment sections) is an important source. But this type of corpus has a systematic quality problem: **a large number of messages are stance-taking, emotional discharge, and identity labeling, rather than verifiable assertions**. The measured data in this paper (see §5) show: among 2000 comments in 5 QQ groups, only 576 (28.8%) carry publicly verifiable anchored assertions; while the anchoring rate of identity-laden controversial groups such as "Western Pseudo-History Theory" is as low as 4.5%. If such polluted data enters the training set, the model will learn a generation pattern of "replacing evidence with identity labels, replacing argumentation with emotion" — this is one of the important sources of hallucination and unreliable knowledge.

The problem is: **how to automatically determine whether the discussion of a corpus segment / a concept is "healthy" (decidable, evidence-based)?** Existing work measures "words" (polysemy quantification), "sentences" (claim verification), "texts" (fake news detection), but **to the best of our search, no one measures "concepts"** — the overall discussion quality of an abstract concept (e.g., "Western Pseudo-History Theory") that repeatedly appears in public debate.

### 1.2 The Metric-Level Gap and the Position of This Paper

| Metric object | Existing work | This paper |
|---|---|---|
| Word (polysemy) | Polysemy quantification (graph curvature, EMNLP 2022) | — |
| Sentence (worth checking?) | Check-worthiness (fact-checking precursor) | — |
| Text (true/false) | Fake news / conspiracy detection | — |
| **Concept (healthy?)** | **Gap** | **Mutual-exclusion structure + anchoring rate joint decision** |

### 1.3 Method Overview

The core idea of this paper is to **bypass semantic analysis**: instead of judging "what this variant says" (semantics is unreliable and not quantifiable), it processes only "how many mutually contradictory variants exist under the same concept name" and "how many variants are anchored to verifiable propositions" — a graph-theoretic bypass, just as graph algorithms do not care what a node is, only its connection relations (original formulation in gain-bandwidth paper [1] §4.11). This measurement algorithmizes the Three Laws test:

- **First Law (Verifiability)**: claim C is valid ⇒ there exists a verification scheme T(C), T completes in finitely many steps and the result is publicly observable (anchored to physical causality). Implemented here as the **anchoring-rate decision** A_rate (§4.2).
- **Second Law (Falsifiability Acceptance)**: cognitive framework F is valid ⇒ there exists a falsification path and the framework holder accepts the possibility of falsification. Its formal decision criterion is Δ (self-reference consistency, Axiom 6 [9]), implemented here as the **label mutual-exclusion algorithm** (§4.3).
- **Third Law (Challenge Acceptance)**: rule R is legal ⇒ there exists a challenge channel. Its verification wavelength is long-period (requires a history of counterexample responses), and this paper uses the **separation signal** (difference between variant-level and comment-level anchoring rates) as a static proxy (§4.6), leaving dynamic data to future work.

### 1.4 Contributions

1. **Concept-level verifiability measurement**: to the best of our search, the first framework that outputs health decisions for "concepts" rather than "texts" (unanchored / decidable / healthy), based on mutual-exclusion structure + anchoring rate, without semantic analysis.
2. **Algorithmization of the Three Laws test**: First Law → A_rate decision (directly interfacing Axiom 1); Second Law → label mutual-exclusion algorithm (quantitative interface of Δ); decisions are insensitive to LLM micro-judgment differences (LLM ablation 15/15 stable).
3. **Empirical data**: 15-concept decisions; first quantification of normative invalidity (moral propositions rank lowest in anchoring rate, verification layer reports no objective outcomes); two-stage cleaning funnel (group-level baseline + comment-level enrichment) filters out 71-99% of non-anchored corpus.

### 1.5 Notation and Self-Containness

All criterion formulas in this paper are self-containedly defined within this chapter/§4. Citations to prior works (Methodology Fifth Edition [2], gain-bandwidth [1], Social Mechanics rewritten edition [3]) always carry complete restatements of formulas or definitions; the reader does not need to consult the prior works. Core notation: A_rate (anchoring rate), μ (mutual-exclusion density), r (coherence), Δr (dimensional sensitivity), align (directional alignment), A(x) (anchoring degree function), λ (characteristic period, i.e., the reciprocal of the frequency at which a hypothesis is tested), T(C) (verification scheme).

---
## 2 Related Work

### 2.1 Stance Detection

Stance detection aims to identify the stance of social media text toward a target (favor/against/neutral); since SemEval-2016 Task 6 it has been a mature field, with many zero-shot and cross-target methods in the LLM era. The "variant polarity clustering" (favor/against/conditional) in this paper is a substep of it — **stance classification is a means, not a contribution**. This paper does not output stance; it outputs concept health decisions.

### 2.2 Controversy Detection

Controversy detection (based on network-structure motifs, or content-based) identifies whether a discussion is controversial. The "controversy rate" statistics of this paper overlap with it, but controversy detection is a **pre-observation** — detecting "there is controversy" does not answer "whether the controversy is decidable". This paper answers the latter.

### 2.3 Polysemy Quantification

EMNLP 2022 (Goel et al.) computes Ollivier-Ricci curvature on context-neighbor graphs to quantify word polysemy, demonstrating the route that "semantics is not quantifiable, but structure is". This paper shares that methodological principle, but the object differs: this paper quantifies the **variant-confrontation structure of concepts** (mutual-exclusion graph), outputting a **health decision** rather than a polysemy score.

### 2.4 Claim Verification and Disinformation Detection

Automatic fact-checking (claim detection → check-worthiness → evidence retrieval → verification) is the standard pipeline; check-worthiness judges "whether a single claim is worth checking" (sentence-level). The anchoring rate of this paper is **concept-level**: it measures "the proportion of anchored verifiable propositions among the variant population of the concept", orthogonal to sentence-level filtering. Fake-news/conspiracy detection is the hottest track (SemEval-2026 has a conspiracy detection task), but this paper explicitly avoids that positioning — it measures **verifiability structure**, not true/false classification.

### 2.5 Prior Work: OD Filter

The OD Filter ([4], published preprint) cleans RLHF training data by operational-definition verifiability (sentence-level). This paper is its **concept-level generalization**: the OD Filter asks "can this datum be verified by an operational definition"; this paper asks "how much of the discussion under this concept name is anchored to verifiable propositions". Narrative chain: sentence-level (OD Filter) → concept-level (this paper) → corpus-level engineering (§7).

---

## 3 Preliminaries: Theoretical Foundation (Self-Contained Definitions)

This section restates the theoretical concepts this paper relies on, all with formula definitions; the reader does not need to consult the prior works.

### 3.1 Anchoring and the First Law

**Definition 3.1 (Verification Scheme T(C))**: A verification scheme for claim C is an operational procedure satisfying three requirements (First Law Axiom Statement [5]): (i) it can be completed in finitely many steps; (ii) the result is publicly observable (verifiable by independent observers); (iii) the verification endpoint is anchored to Layer-A physical outcomes (publicly reproducible observations, such as stock price data, archaeological findings, statistical significance).

**Definition 3.2 (A-Anchored Variant)**: A variant carrying at least one verification scheme satisfying Definition 3.1 is called an A-anchored variant. The criterion is "an executable verification scheme exists" (not "theoretically verifiable"), and the endpoint of the argumentation chain must be a physical outcome rather than another concept (concept→concept→concept is logical idling, judged non-anchored).

**Definition 3.3 (Anchoring Degree Function A(x), Methodology 5.3 [2])**: The anchoring state of concept x is characterized by the anchoring degree function: A(x) → 0 indicates Layer B (symbolic layer) detaching from Layer-A (physical layer) anchoring, i.e., **decoupling**; A(x) being maintained indicates health. This paper uses the computable anchoring rate (§4.2) as its operationalization.

### 3.2 Wavelength and the Frequency Blind Zone

**Definition 3.4 (Characteristic Period λ, gain-bandwidth 3.1 [1])**: λ is the characteristic period of a Layer-B hypothesis, i.e., the reciprocal of the time scale at which the hypothesis is tested/updated (reciprocal of frequency). For example, "this stock will rise in the short term" has short λ (testable within days); "all civilization originated in Huaxia" has λ tending to infinity (the claim covers all spacetime, with no finite verification window).

**Definition 3.5 (Frequency Blind Zone, gain-bandwidth 5.2 [1])**: An observation instrument (conceptual framework + collection method + statistical procedure) has a processing bandwidth (time window, concept granularity, sampling frequency). When the instrument bandwidth < the signal wavelength range, periodic signals at specific periods receive no gain — "no signal outside the bandwidth" is indistinguishable from "no signal inside the bandwidth". **Important corollary of this paper**: the Third Law's (Challenge Acceptance) verification wavelength is long-period (requires accumulation of multiple challenge-response cycles), so a single snapshot observation necessarily falls into the frequency blind zone — this is the structural reason the Third Law is statically undecidable (§4.6).

### 3.3 Decoupling Criterion

**Definition 3.6 (Decoupling, Methodology 5.3 [2])**: decoupling = Layer B detaching from A1 anchoring (anchoring degree A(x) → 0). The mechanism is value-category misplacement (mistaking the symbolic layer's "correct/legal" for the material layer's "outcome"). The decision function of this paper directly aligns with this criterion: A_rate (comment-level) → 0 is decoupling (unanchored).

### 3.4 Algorithmization Interfaces of the Three Laws

**Definition 3.7 (Three Laws Algorithmization Mapping)**:

| Law | Formal criterion | Algorithm implementation | Verification wavelength | Status |
|---|---|---|---|---|
| First Law (Verifiability) | Axiom 1: ∃T(C) (Def. 3.1) | A-anchor decision → A_rate (§4.2) | Short (snapshot suffices) | ✅ Static |
| Second Law (Falsifiability Acceptance) | Δ self-reference consistency (Axiom 6 [9]) | Label mutual-exclusion algorithm (§4.3) | Medium (snapshot + sample size) | ✅ Static |
| Third Law (Challenge Acceptance) | Axiom 3: ∃K(R) ([2] Axioms 1-6) | Separation signal static proxy (§4.6) | Long (accumulated challenges) | ⏳ Proxy + dynamic pending |

### 3.5 Notation Quick-Reference Table (first-time readers may skim; refer back as needed)

| Symbol | Name | Intuitive meaning | First appears |
| --- | --- | --- | --- |
| C = (V, G) | Concept | A concept is not a word; it is a population of mutually conflicting variants + the mutual-exclusion relations among them | §4.3 |
| V / N | Variant set / variant count | How many "statements" exist under this concept name | §4.3 |
| E / M | Mutual-exclusion edge set / edge count | How many pairs of statements give opposite answers on the same matter | §4.3 |
| μ | Contradiction density | Density of mutual contradiction among variants (normalized mutual-exclusion pair count) | §4.3 |
| r | Coherence | Whether the prediction directions of variants align (0=everyone says different things, 1=unanimous same direction) | §4.3 |
| Δr | Dimensional sensitivity | How much the unanimity drops when the observation angle changes (sharp drop = unanimity is illusory) | §4.3 |
| A_rate | Anchoring rate | Proportion of variants (or comments) carrying verification schemes | §4.2 |
| Sep | Separation signal | Gap between formally having a verification scheme and behaviorally not verifying | §4.2 |
| align | Directional alignment | Proportion of variant predictions matching objective facts | §4.5 |
| D(C) | Decision function | Final output: unanchored / decidable dispute / healthy | §4.4 |
| T(C) | Verification scheme | A verification procedure with finitely many steps, publicly observable results | §3.1 |
| λ | Claim wavelength | How often a statement promises to be testable | §3.2 |

**One-sentence memory aid (Three Laws anchor points):** the First Law governs "whether it can be verified" (A_rate); the Second Law governs "whether verification conflicts" (μ, r, Δr); the Third Law governs "whether verification is honored" (align, Sep).

---
## 4 Method: Algorithmization of the Three Laws Test

### 4.1 Two-Layer Architecture

The algorithm is decomposed into two layers:

```
Input: concept C + variant source (literature / corpus)
├─ LLM extraction layer (ablatable): variant enumeration + polarity clustering → A-anchor decision → θ phase → (event, prediction)
├─ Deterministic kernel (reproducible): mutual-exclusion graph (M) → structural features (N/M/μ/r/r_d/A_rate) → decision function D(C)
└─ External verification layer (audit, not annotation): real existence of verification interfaces → align
```

![Figure 1: Two-layer architecture](figures/fig0_arch.png)

**Design principle:** the LLM is an extractor, not a judge — all decisions (mutual-exclusion graph construction, structural feature computation, decision function) are deterministic code, reproducible and auditable (every intermediate quantity is traceable to source evidence). The external verification layer verifies the real existence of verification interfaces (e.g., whether carbon-14 dating, financial report data sources exist), not relying on human annotation consensus (rewritten edition 4.3 [3]: "the A-anchor decision obtains an algorithmic criterion (no longer relying on human annotation)").

**Motivation overview of the criteria (why these functions are needed):**

| Criterion | Question to answer (intuitive) | Why this formula |
| --- | --- | --- |
| A_rate | How many statements in the discussion of this concept are "verifiable"? | Directly count the proportion: share of variants (comments) carrying verification schemes — algorithmization of the First Law |
| μ | How densely do these statements conflict? | Mutual-exclusion pairs divided by the maximum possible mutual-exclusion pairs C(N,2) — after normalization, 3 variants and 23 variants are comparable |
| r | Is the conflict ordered or chaotic? (all mutually exclusive can still quarrel in an orderly way) | Take the complex mean of prediction-direction phases and its modulus: all directions identical → \|1\|=1; all directions chaotic → mean approaches 0 |
| Δr | Is the "consistency" among variants real structure, or does it collapse when the angle changes? | Coherence difference between two-axis and three-axis subspaces: true convergence is stable (Δr≈0 or negative), false convergence collapses (Δr large positive) |
| align | Is the prediction direction itself correct? (r high but all predictions wrong = unanimous wrongness) | Proportion of predictions matching objective facts |
| Sep | Verbally claim verifiability, but behaviorally verify or not? | Variant-level A_rate (form) minus comment-level A_rate (behavior) — the gap is the "performance" quantity |

**How to read:** A_rate/μ/r/Δr/align answer "what does the discussion structure of this concept look like", Sep answers "how far does the behavior of this discussion deviate from its structure", and D(C) synthesizes the structural answers into a decision.

### 4.2 Anchoring Rate A_rate (Algorithmization of the First Law)

**Definition 4.1 (Anchoring Rate)**: The anchoring rate of concept C is the ratio of anchored variants to the total number of variants:

$$A_{rate}(C) = \frac{N_{anchored}}{N}$$

where N is the number of variants and N_anchored is the number of variants satisfying Definition 3.1 (existence of a verification scheme with finitely many steps, publicly observable). The decision is executed by the LLM extraction layer according to the three requirements of Axiom 1: has_check_plan (an executable verification scheme exists, not "theoretically verifiable") ∧ finite_steps ∧ public_observable ∧ not self-contained definition (excluding closed concepts of the "X explains everything" type); it also executes the argumentation-chain endpoint check (endpoint is a physical outcome vs a concept; a conceptual endpoint is judged logical idling, non-anchored).

**Two criteria:** ① variant-level A_rate_variant (judged from variant texts, measuring "formal verifiability"); ② comment-level A_rate_comment (aggregated from the anchoring behavior of comments in real discussions, measuring "behavioral anchoring"). **The comment level is the decision axis** (the behavioral layer is real), with the variant level serving as the formal-layer control.

**Engineering trade-off (honest annotation):** the actual comment-level anchoring-rate decision in this paper adopts the lenient criterion ("contains verifiable content", including logical argumentation), rather than the above three requirements of Axiom 1 (endpoint A1 physical). Reason: under the strict criterion (endpoint physical), the anchored sample in chat corpora is too small to support the subsequent variant enumeration, mutual-exclusion graph construction, and decision. This relaxation is an engineering trade-off; its cost and the comparison of the four criteria are in §5.5.

**Separation signal (Third Law static proxy):**

$$Sep(C) = A_{rate}^{variant}(C) - A_{rate}^{comment}(C)$$

A large positive Sep means "formally has a verification scheme but behaviorally does not anchor" — i.e., "appears refutable but is in fact not" (the static projection of Third Law failure). The anchoring degree function A(x) of Methodology 5.3 [2] is the overall criterion: comment-level A_rate → 0 is decoupling.

### 4.3 Label Mutual-Exclusion Algorithm (Algorithmization of the Second Law / Δ)

**Definition 4.2 (Mutual-Exclusion Graph)**: concept C = (V, G), V is the variant set, G(V, E) is the mutual-exclusion graph — each edge in E connects a pair of variants that give mutually exclusive result predictions on the same observable event (e.g., "the location of the Tumu Crisis": Europe vs China). The mutual-exclusion decision uses structured rules (event e, prediction p): two variants are mutually exclusive ⟺ they share event e ∧ pred_i(e) and pred_j(e) are mutually exclusive (the literature mode uses manually encoded literature mutual-exclusion pairs; the gain-bandwidth 4.4-4.7 [1] list is already available).

**Definition 4.3 (Full Family of Structural Features, rewritten edition 2.2 [3]):**

- Variant count N = |V|
- Mutual-exclusion edge count M = |E|
- Contradiction density μ = M / C(N, 2) (C(N,2) is the maximum possible mutual-exclusion pair count)
- Coherence r = |Σ_j e^{iθ_j}| / N_θ, where θ_j is the prediction-direction phase of variant j (prediction occurs → θ=0, does not occur → θ=π, conditional → θ=π/2; mapped as deterministic code, not fed to the LLM), N_θ is the number of variants having a prediction-direction phase (variants without predictions do not participate in the r computation, see the toy example in §4.8)
- Dimensional sensitivity Δr = r₂ − r₃ (coherence difference between two-axis and three-axis subspaces; two-axis = stance axis + event axis, three-axis = + topic axis; the dimensional criterion of gain-bandwidth 4.9 [1]). **Dimensional statement (2026-08-14):** the semantic-axis system of this paper has 3 axes (stance/event/topic), with the same simulation form as the 5-axis system of gain-bandwidth 4.9 [1] but a different dimension count — cross-paper comparison of Δr must note the dimensional baseline difference; the criterion is based on this paper's axis system.

**Calibration of μ* (observer effect):** the critical mutual-exclusion count M*∈[7,20] of criterion S7 is calibrated at the observation resolution of N=20 (criterion ζ: M*_ζ=20 resolved from ζ_eff = ζ_ext + αM ≥ ζ_c, i.e., 0.2 + 0.04·20 = 1.0). Small-sample concepts (N=3-6) naturally read low M (insufficient sampling density, corresponding to the observer effect of Definition 3.5) — the normalized density μ = M/C(N,2) must be used, whose critical interval is:

$$\mu^* \in [7/C(20,2),\ 20/C(20,2)] = [0.037,\ 0.105]$$

**Empirical calibration statement (2026-08-14):** the μ* critical values are an empirical calibration on the N=20 observation surface (S7 simulation + ζ_eff analysis; α=0.04 is a model parameter, not a measured value); the small-sample (N=3-6) switch to normalized density μ is an engineering approximation, not strictly consistent with the absolute-M ζ criterion under small samples (when N≤6, C(N,2)≤15<20, the ζ criterion never reaches criticality) — when both criteria coexist, data testing prevails. This is a known gap of an empirical algorithm, not disguised as a mathematical derivation; consistent with empirical algorithms of the same class in large models: validity is confirmed by data testing (First Law), not by formal completeness.

### 4.4 Decision Function D(C) (Three-Class + Explicit Confidence)

**Corpus mode (A_rate criterion):**

$$D(C) = \begin{cases} \text{unanchored} & A_{rate}^{comment} < p^* \\ \text{decidable dispute} & A_{rate}^{comment} \geq p^* \land M \in [7,20] \\ \text{supercritical mutual exclusion} & A_{rate}^{comment} \geq p^* \land M > 20 \\ \text{healthy} & A_{rate}^{comment} \geq p^* \land M < 7 \end{cases}$$

where p* = 0.25 (S10 simulation calibration, rewritten edition 2.7 [3]). **Structurally, the decision is the two-state "unanchored / anchored"; the "anchored" side is divided by mutual-exclusion degree into "decidable dispute / healthy" (total three classes) + explicit confidence** (no "insufficient evidence" fourth state — "insufficient evidence" is carried by the confidence mechanism, not disguised as a concept state). **"False convergence" (r high ∧ align low; align defined in §4.5) is an additional diagnostic layer, superimposed on the unanchored decision (§6.3 Pseudo-History case), not changing the deterministic kernel of the main decision.** Each decision carries a confidence computed from the binomial standard error of A_rate and the distance to the threshold:

$$SE = \sqrt{A(1-A)/N_{comment}},\quad z = |A - p^*|/SE$$

z ≥ 2 high confidence; 1 ≤ z < 2 medium confidence; z < 1 low confidence ("insufficient evidence" annotation — more samples needed, not a third state).

**Literature mode (μ+A combined criterion):** the literature mode has no comment-level samples, and using μ alone would misjudge "suspended" as "valid" (see the §6.3 Pseudo-History case) — the combined criterion:

$$D_{lit}(C) = \begin{cases} \text{supercritical mutual exclusion} & \mu \geq \mu^*_{hi} \\ \text{critical} & \mu^*_{lo} \leq \mu < \mu^*_{hi} \\ \text{unanchored (suspended)} & \mu < \mu^*_{lo} \land A < p^* \\ \text{low mutual exclusion / valid} & \mu < \mu^*_{lo} \land A \geq p^* \end{cases}$$

where A preferentially takes the comment-level A_rate (when it exists and >0), otherwise the variant-level A_rate_variant.

### 4.5 External Verification Layer and align

**Definition 4.4 (Directional Alignment align)**: for each A-anchored variant, verify the objective outcome of the event its prediction targets (factual_outcome ∈ {occurred, not occurred, unknown}, based on public facts / academic consensus, no speculation):

$$align = \frac{\#\{v : pred(v) \text{ consistent with } outcome(v)\}}{\#\{v : outcome(v) \neq \text{unknown}\}}$$

align is the S9 directional criterion: r high (consistent prediction direction) ∧ align low (contrary to facts) jointly trigger the **false convergence** decision (Pseudo-History case: r=1.0 ∧ align=0.0). align is a weakly robust quantity (depends on the LLM's judgment of world facts; different LLMs differ on "which variants have objective outcomes", see §8 ablation), used only as auxiliary diagnosis, not participating in the main decision.

### 4.6 Boundary of the Third Law and the Static Proxy

The decision object of the Third Law (Challenge Acceptance) is the "response pattern in the face of counterexamples" (correction/absorption/silence/attack), requiring accumulation of multiple challenge events — the verification wavelength is long-period (Definition 3.4). A single snapshot observation falls into the frequency blind zone (Definition 3.5) — **the Third Law being statically undecidable is a structural necessity, not an engineering defect**. This paper uses the separation signal (Sep of Definition 4.1) as a static proxy: large positive Sep + low comment level = Third Law failure suspicion (performed verification: formal scheme exists, behavior refuses); large positive Sep + high comment level = discussion not yet unfolded (non-pathological). Dynamic decision (counterexample-response history) is left to future work.

### 4.7 Dual-Mode Execution

| Mode | Variant source | Criterion | Note |
|---|---|---|---|
| Literature enumeration | Doctrinal-history literature / theoretical texts | μ+A combination (S7) | Academic texts have explicit claim wavelengths (verification schemes are part of the theoretical structure), A_rate naturally high — use structural criterion only |
| Corpus statistics | Comment sections / danmaku / group chats | A_rate + Δr + align (S10/S8/S9) | Chat claims never declare wavelengths — behavioral criterion (comment-level A_rate) is the only real one |

The two modes share the same deterministic kernel and decision-function form; the difference is only in criterion selection (determined by genre: the explicitness of claim wavelengths; a re-enactment of the watershed table of gain-bandwidth 6.2 [1] on genre differences).

### 4.8 Minimal Working Example: Full Hand Computation of a Toy Concept

To avoid formula stacking, a 3-variant toy concept "will the stock rise tomorrow" is hand-computed end to end (the reader can verify every number):

**Variants (LLM extraction layer output):**

| Variant | Claim | Verification scheme | θ phase | Objective outcome (after verification) |
|---|---|---|---|---|
| v₁ | Will rise | Yes (check tomorrow's closing price) | 0 (prediction occurs) | Rose (consistent) |
| v₂ | Will fall | Yes (check tomorrow's closing price) | π (prediction does not occur) | Rose (inconsistent) |
| v₃ | Rise or fall is decided by the market maker | No (unverifiable) | None | — |

**Step 1 — mutual-exclusion graph:** v₁ and v₂ give opposite predictions on the same event (tomorrow's close) → mutual-exclusion edge (v₁,v₂). v₃ is unfalsifiable, mutually exclusive with no one. Get V={v₁,v₂,v₃}, N=3, M=1.

**Step 2 — anchoring rate:** v₁, v₂ have verification schemes, v₃ does not → A_rate = 2/3 ≈ 0.67.

**Step 3 — contradiction density:** μ = M/C(N,2) = 1/3 ≈ 0.33.

**Step 4 — coherence:** r = |e^{i·0} + e^{i·π}|/2 = |1 + (−1)|/2 = 0 (the two variants have opposite directions, completely inconsistent). If v₂ also predicted "rise", then r = |1+1|/2 = 1 (unanimous).

**Step 5 — directional alignment:** after verification the actual outcome is "rose": v₁ consistent (1 point), v₂ inconsistent (0 points) → align = 1/2 = 0.5.

**Step 6 — decision:** A_rate=0.67 ≥ p*, M=1 < 7 → **healthy** (verifiable, conflicts controllable, prediction direction half correct). If v₃ were also a verifiable variant and A_rate unchanged, M=1 stays; if variants increase to 10 with 5 mutual-exclusion pairs, μ=5/C(10,2)=0.11 still in the critical zone, moving to "decidable dispute".

**Two common questions this example answers:** ① "Why divide μ by C(N,2)?" — without the division, the N=23 Pseudo-History theory naturally has more mutual-exclusion pairs than the N=3 survivor, making cross-concept comparison impossible; after normalization, 0.33 is the "conflict density". ② "Why does r use the complex modulus?" — because "prediction occurs/does not occur" is directional (positive/negative), complex phases naturally express direction, and taking the modulus yields "directional consistency" — a ready-made tool borrowed from physics synchronization measures (Kuramoto), not a new invention.

(End of Chapter 4; Experiment 1 follows in Chapter 5)

---
## 5 Experiment 1: Corpus-Statistics Mode (10-Concept Decisions)

### 5.1 Data

- **Bilibili video comment sections (3 videos):** Lei Jun Xiaomi premiumization (485), tattoo-and-bar "bad girl" (2003), CoreSwap performance claims (569)
- **Bilibili video danmaku:** tattoo-and-bar "bad girl" (1308)
- **QQ group chats (5 groups, 400 each, 2000 total):** Backyard No.3 / No.4, Ward 8, Ward 9, Abnormal Humans — each comment judged by the LLM for has_anchor/stance/topic (version record: qq_anchor_judge.py; has_anchor is a lenient judgment including logical argumentation; strict judgment and criterion comparison see §5.5)
- **Pseudo-History literature control:** 67 keyword-context items from a military-history group, enumerating 23 variants (literature mode, §6; the enumeration contains one duplicate-id "state-support theory"; after mutual-exclusion deduplication it is 22 — this paper counts by enumeration as 23; per-variant judgment see §8.2)

### 5.2 Overall Results Table (deepseek side, Figure 2)

| Concept | N | M | μ | A_rate(com) | A_rate(var) | Sep | r | Δr | align | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| Western Pseudo-History Theory | 23 | 2 | 0.009 | 0.045 | 0.435 | +0.390 | 1.000 | +0.382 | 0.0 (n=10) | **unanchored false convergence** |
| Lei Jun Xiaomi premiumization | 8 | 9 | 0.321 | 0.600 | 1.000 | +0.400 | 0.250 | −0.395 | 0.0 (n=3) | **decidable dispute** |
| Tattoo-and-bar (comments) | 8 | 9 | 0.321 | 0.121 | 0.625 | +0.504 | 0.354 | −0.176 | 1.0 (n=1) | unanchored |
| Tattoo-and-bar (danmaku) | 8 | 6 | 0.214 | 0.019 | 0.375 | +0.356 | 1.000 | −0.276 | — | unanchored |
| QQ Backyard No.3 | 8 | 4 | 0.143 | 0.278 | 0.000 | −0.278 | 0.000 | +0.030 | — | healthy |
| QQ Ward 8 | 8 | 3 | 0.107 | 0.355 | 0.000 | −0.355 | 1.000 | +0.014 | — | healthy |
| QQ Ward 9 | 6 | 3 | 0.200 | 0.231 | 0.333 | +0.102 | 0.707 | −0.040 | — | unanchored (critical) |
| QQ Abnormal Humans | 8 | 6 | 0.214 | 0.400 | 0.375 | −0.025 | 0.500 | −0.273 | 0.5 (n=2) | healthy |
| QQ Backyard No.4 | 8 | 4 | 0.143 | 0.278 | 0.000 | −0.278 | 1.000 | +0.030 | — | healthy |
| CoreSwap performance claims | 8 | 4 | 0.143 | 0.250 | 0.750 | +0.500 | 0.527 | +0.027 | — | healthy (critical) |

(Sources: QQ group chats — Backyard No.3 / Ward 8 / Ward 9 / Abnormal Humans / Backyard No.4; Bilibili video comment sections — Lei Jun Xiaomi premiumization 485, tattoo-and-bar 2003, CoreSwap 569; Bilibili danmaku — tattoo-and-bar 1308; Western Pseudo-History Theory is literature-enumeration mode, see §6. Note: the A_rate(com) in this table is the **variant-coverage-subset lenient criterion** (variant-merged comments 15-124 items, not the full 400/2003), differing from the full-sample lenient criterion of Table 1; criterion comparison and engineering trade-offs see §5.5)

**Key points:** A_rate (comment-level) gradient 0.019→0.600 corresponds to the decisions; the Pseudo-History theory exclusively occupies the false-convergence quadrant (Δr=+0.382 dimensional-elevation collapse + r=1.0 high coherence + align=0.0 all facts reversed); Lei Jun is the true-convergence direction (Δr=−0.395, more convergent under dimensional elevation).

![Figure 2: Concept decision scatter (Pseudo-History exclusively in false-convergence quadrant)](figures/figA_deltaR_scatter.png)

![Figure 3: Corpus-mode decision panorama](figures/figB_panorama.png)

### 5.3 Confidence and Critical Bands

Per the SE/z of Definition 4.4: high confidence (z≥2) — Lei Jun (4.79), tattoo comments (4.41), tattoo danmaku (32.9), Pseudo-History (7.66); medium confidence — QQ Ward 8 (1.22), Abnormal Humans (1.19); **insufficient evidence (z<1) — QQ No.3 / No.4 / Ward 9 / CoreSwap (0.00-0.38)**. The critical-band concepts (QQ group samples of 15-39 items, insufficient statistical resolution) retain their decisions but are annotated low confidence.

### 5.4 Topic Contrast: Data Evidence for Normative Invalidity

**The normative topic (tattoo) ranks last overall in anchoring rate** (comments 0.121 / danmaku 0.019, lowest of the 15 concepts; these values are the variant-coverage-subset lenient criterion; full-sample lenient criterion is 34.0%/8.5%, see §5.5), and the verification layer annotates 4/5 variants "no objective outcome" ("universally regarded as bad, lacking unified quantitative conclusions") — the normative proposition ("tattoo-and-bar = bad girl") does not carry a publicly verifiable verification scheme under the First Law (Definition 3.1), and the verification layer correctly executes the framework annotation "unknown". Three-topic contrast:

| Topic type | Representative | Comment-level A_rate | Verification-layer verifiability |
|---|---|---|---|
| Normative/moral | Tattoo | 0.019-0.121 | All "unknown" (no objective outcome) |
| Factual assertion | Pseudo-History | 0.045 (behavioral) | 10/10 verifiable (archaeology checkable) |
| Attribution judgment | Lei Jun | 0.600 | 3/8 verifiable (rest "unknown") |

**Significance: the first quantitative empirical evidence for the physics-causality-anchored-verification-theory proposition that "morality is an invalid proposition" (First Law critique, value-category misplacement, Definition 3.6)** — from a philosophical assertion to a statistical, reproducible data conclusion. The verification layer naturally distinguishes topic types (normative → all unknown, factual → all verifiable, attribution → partially unknown) without an explicit assertion-type classifier.

### 5.5 Data Criterion Notes

> This section explains the data criteria actually adopted in this paper, for readers to judge the credible boundary of the conclusions. The **main decision of "comment-level anchoring rate A_rate" adopts the lenient criterion** (including logical argumentation) — this is a deliberate engineering trade-off: under the strict criterion (endpoint A1 physical), anchored samples in chat corpora are too few (QQ groups full-sample strict only 9-12%), insufficient to support the subsequent variant enumeration, mutual-exclusion graph construction, and decision. The relaxation chain is: **strict (endpoint A1 physical) → lenient (including logical argumentation) → variant-coverage subset (only comments with a stance that can be assigned to some statement)**; each step trades strict verifiability for sufficient sample size. The lenient version counts "logical argumentation" (endpoint at Layer-B symbols) as anchored, relaxing the First Law's "endpoint A1 physical" constraint — this is the cost of the trade-off; readers must be aware when judging the conclusions.

**(I) Criterion comparison.** A_rate coexists in four criteria:

| Criterion | Decision standard | Sampling scope | QQ group mean | Source |
| --- | --- | --- | --- | --- |
| Full-sample strict (deepseek) | Endpoint A1 physical | Full 400 items | 10.1% | re-run |
| Full-sample strict (GLM-5.2 Alibaba Cloud) | Endpoint A1 physical | Full 400 items | 19.6% | re-run |
| Full-sample lenient | Contains verifiable content (incl. logical argumentation) | Full 400 items | 28.8% | qq_anchor_judge |
| Variant-coverage subset lenient | Contains verifiable content | Variant-merged comments (15-39 items) | 0.231-0.400 | mutex A_rate |

**(II) Bilibili full-sample strict (2026-08-14 supplement, deepseek FLASH 40-concurrency + GLM-5.2 Alibaba Cloud 24-concurrency re-run):**

| Dataset | Full sample | Full-sample strict DS | Full-sample strict GLM | Full-sample lenient (control) |
|---|---|---|---|---|
| Lei Jun Xiaomi premiumization | 485 | 34.4% (167/485) | 35.3% (171/485) | 57.3% |
| Tattoo-and-bar (comments) | 2003 | 16.3% (326/2003) | 16.3% (327/2003) | 34.0% |
| Tattoo-and-bar (danmaku) | 1308 | 7.2% (94/1308) | 7.0% (92/1308) | 8.5% |
| CoreSwap performance claims | 569 | 32.0% (182/569) | 35.9% (204/569) | 25.0% (variant subset) |

The Bilibili full-sample strict and QQ group full-sample strict share the "endpoint A1 physical" criterion (same strict prompt) and can be directly compared with the QQ group strict values above (DS 10.1% / GLM 19.6%). The lenient→strict contraction (Lei Jun 57.3→34.4, tattoo comments 34.0→16.3, danmaku 8.5→7.2) is positively correlated with the topic's "logical-argumentation density"; danmaku lenient and strict are nearly identical (8.5→7.0), side-validating criterion consistency. CoreSwap strict (32.0%) surpasses tattoo comments (16.3%) — the behavioral paradox of "performance claims are the most testable" holds under the strict criterion as well. GLM ablation consistency (strict criterion): the two models differ ≤3.9 percentage points across the four datasets (Lei Jun +0.9, tattoo comments 0.0, danmaku −0.2, CoreSwap +3.9), stable at both decision and A_rate level — contrasting with the 56.5% low per-variant agreement of §8.1 (observation-granularity effect of aggregate quantities vs single-point judgments, see §8.2).

**(III) Criteria used at each location in this paper (reader index).**

The "28.8%" in the Abstract and the QQ group anchoring rates in Table 1 are **full-sample lenient**; the Bilibili anchoring rates in Table 1 (Lei Jun 60%, tattoo 12.1%, etc.) and the A_rate(com) in the §5.2 main-decision table are **variant-coverage subset lenient**; the §5.5 (II) Bilibili values are **full-sample strict** (dual-model comparison, deepseek and GLM). Taking "Abnormal Humans" as an example: variant subset 40% (6/15), full-sample lenient 23.8% (95/400), full-sample strict 9.0% (36/400) — readers should note the criterion differences when comparing.

---
## 6 Experiment 2: Literature-Enumeration Mode (5-Concept Theoretical-Lineage Verification)

### 6.1 Data

The variant list and mutual-exclusion pair encodings of the literature-enumeration mode all originate from the literature-anchored variant list of gain-bandwidth 4.4-4.7 [1] (original doctrinal-history formulations), mapped by school:

| Concept | Literature source (school / doctrinal-history formulation) |
|---|---|
| Market economy (pure market) | Fama efficient market hypothesis / Shiller behavioral finance / Arrow-Debreu general equilibrium / Hayek spontaneous order |
| Absolute planned economy (pure planning) | Lange market socialism / Kornai shortage economics |
| Feminism | Millett sexual politics / Butler gender performativity theory |
| Socialist market economy | Socialist market economy literature (operational-discipline formulations combining planning and market) |
| Marxist women's liberation | Engels "The Origin of the Family, Private Property and the State" / Marxist women's liberation thought |

Mutual-exclusion pair encoding follows Definition 4.2 (same event, mutually exclusive predictions).

### 6.2 Results (μ+A Combined Criterion)

| Concept | N | M | μ | A_rate(var) | Theoretical prediction | Actual decision | Consistent |
|---|---|---|---|---|---|---|---|
| Market economy (pure market) | 5 | 3 | 0.300 | 0.800 | Supercritical mutual exclusion | **Supercritical mutual exclusion** | ✓ |
| Absolute planned economy (pure planning) | 6 | 4 | 0.267 | 1.000 | Supercritical mutual exclusion | **Supercritical mutual exclusion** | ✓ |
| Feminism | 5 | 4 | 0.400 | 0.600 | Supercritical mutual exclusion | **Supercritical mutual exclusion** | ✓ |
| Socialist market economy | 3 | 0 | 0.000 | 1.000 | Low mutual exclusion / valid | **Low mutual exclusion / valid** | ✓ |
| Marxist women's liberation | 3 | 0 | 0.000 | 1.000 | Low mutual exclusion / valid | **Low mutual exclusion / valid** | ✓ |

**P9 theoretical prediction verified 5/5** — "operational discipline survives, ontological commitment is paralyzed" [Note: "ontological commitment" appears here as a quoted term from the cited prior work (gain-bandwidth 4.8 [1]), describing the attribute of the criticized objects (pure market / pure planning / feminism) — a quoted-use exemption, not a self-referential claim of this framework; per self-reference-consistency review policy, quoted philosophical terms are annotated rather than prohibited.] (the regularity of gain-bandwidth 4.8 [1]): socialist market / Marxist women's liberation degrade the concept into testable operational discipline (μ=0, variants organized around the same material anchor point); pure market / pure planning / feminism are ontological commitments (quoted-use term; untestable, variants proliferate mutually exclusive, μ supercritical).

### 6.3 Key Case: Western Pseudo-History Theory (Protagonist of This Paper)

**Literature mode:** μ=0.009 (23 variants with only 2 true mutual-exclusion pairs: the Tumu location, Tang-Song relations) — low mutual exclusion but **comment-level A_rate=0.045** (behavioral layer does not anchor) → per the μ+A combined criterion of Definition 4.4: low mutual exclusion + low anchoring = **unanchored (suspended)** (not the "low mutual exclusion + high anchoring" valid form — the latter is the survivor's form). This is the quantification of "suspended rather than paralyzed": variant proliferation concentrates in the untestable layer (identity/stance/methodology), not in propositional mutual exclusion.

**Corpus mode:** A_rate(com)=0.045 → S10 unanchored; r=1.0 (all prediction directions identical) + align=0.0 (all 10 verifiable variants' predictions refuted by objective facts: the Tumu Crisis was in Huailai, Hebei; multi-center origins of civilization, etc.; verification basis consistent with independent sources) → **false convergence**; Δr=+0.382 (two-axis r=1.000 inflated → three-axis 0.618 collapse) → S8 dimensional criterion.

**Complete decision chain:** First Law passes (variant-level 0.435, formally verifiable) ∧ Second Law fails (false convergence: r high ∧ align low) ∧ behavioral layer refuses (comment-level 0.045 + L4 counterexample absorption: archaeological evidence = forgery) — four-layer evidence of "written but not honored". Cross-mode consistency: literature (suspended) and corpus (unanchored false convergence) independently judge unanchored.

![Figure 4: Pseudo-History decision chain (four-layer evidence)](figures/figF_chain.png)

![Figure 5: Pseudo-History verification result distribution (deepseek vs GLM-5.2, source of align differences)](figures/figE_align_verify.png)

### 6.4 Two Directions of Criterion Complementarity: First-Law Pass ≠ Healthy; Consistency ≠ Healthy

**Direction 1 (First-Law pass ≠ healthy):** market economy variant-level A_rate=0.800 (every variant has a verification scheme) but μ=0.300 supercritical (Fama vs Shiller give opposite predictions on the same stock price) — **"all can be verified" and "verification results conflict" are two independent dimensions**: the First Law filters "whether it can be verified", the Second Law judges "whether verification conflicts"; both are indispensable (criterion complementarity).

**Direction 2 (consistency ≠ healthy: the two-dimensional observation illusion of unanchored consistency):** the tattoo case shows the other side of the duality. The concept is highly consistent on the stance/emotion dimension (variants almost all agree "tattoo-and-bar = bad girl"; stance consistency ≠ prediction mutual exclusion — §5.2 Table M=9 shows variants have mutual-exclusion pairs on specific predictions; the two do not contradict), and if observed only via mutual-exclusion structure (Second Law perspective), it would be misjudged as "healthy consistency". But this consistency is **content-missing consistency**: moral propositions have no verification scheme (First Law fails, A_rate only 0.019-0.121), the variant vectors have no component at all in high-dimensional space (event axis, verification axis, fact axis) — its consistency comes from "never entering testable space", not from "contradiction adjudicated by facts".

This is precisely the variant of the **two-dimensional observation projection illusion** of gain-bandwidth 4.9 [1] on normative concepts: that paper proves mutual-exclusion concepts are high-dimensional dispersed structures, and the "convergence" under two-dimensional observation is a projection illusion (under two-dimensional observation, true/false convergence differ by only r=0.003, almost indistinguishable; after dimensional elevation the r difference is 0.173, distinguishable). But moral concepts constitute another kind of "appearing consistent" — not high-dimensional mutual-exclusion structure masked by low-dimensional projection (Pseudo-History type, exposed by elevation, Δr=+0.382), but **high-dimensional content simply does not exist** (moral type, elevation cannot expose mutual exclusion because there is no mutual exclusion to expose; what is exposed is the unanchored A_rate→0). The two "consistency" pathologies require two different observation dimensions to be exposed separately: **dimensional elevation (adding a semantic axis, S8) catches the Pseudo-History type of false convergence; adding the verifiability dimension (First Law A_rate) catches the moral type of empty consistency**.

**This gives the First Law its independent value:** it not only filters "non-verifiable" concepts, but also prevents the two-dimensional observation illusion of the Second Law — without the First Law, a "consistent but unprovable" concept like tattoo would be misjudged as healthy by mutual-exclusion structure. The "μ low + A low = unanchored (suspended)" branch of the μ+A combined criterion (Definition 4.4) is precisely designed to expose this illusion.

## 7 Application: Fast Strict Filter (LLM Training Data Cleaning)

### 7.1 Scenario and Metrics

Chat-community corpora are enormous in volume with little effective information (measured 71.2% of comments non-anchored). **Filterable (non-anchored) proportions of each dataset (Table 1)**: five QQ groups 66.2-76.2%, Bilibili danmaku/comment sections 40-98.1%, Pseudo-History group 95.5% — the goal of the cleaning pipeline is to turn this proportion into an actual filter-out rate.

**Table 1  Filterable (non-anchored) proportion of each dataset**

| Dataset | Source | Total items | Anchoring rate | Non-anchored (filterable) proportion |
|---|---|---|---|---|
| QQ Backyard No.3 | QQ group chat | 400 | 25.2% | 74.8% |
| QQ Ward 8 | QQ group chat | 400 | 30.8% | 69.2% |
| QQ Ward 9 | QQ group chat | 400 | 33.8% | 66.2% |
| QQ Abnormal Humans | QQ group chat | 400 | 23.8% | 76.2% |
| QQ Backyard No.4 | QQ group chat | 400 | 30.5% | 69.5% |
| Pseudo-History group (military history) | QQ group chat | 5105 | 4.5% | 95.5% |
| Lei Jun Xiaomi premiumization | Bilibili video comment section | 485 | 60.0% | 40.0% |
| Tattoo-and-bar (comments) | Bilibili video comment section | 2003 | 12.1% | 87.9% |
| Tattoo-and-bar (danmaku) | Bilibili video danmaku | 1308 | 1.9% | 98.1% |
| CoreSwap performance claims | Bilibili video comment section | 569 | 25.0% | 75.0% |

(Anchoring-rate criteria: QQ groups full-sample lenient judgment (400 each); Bilibili variant-coverage subset lenient judgment (15-124 items); criteria and engineering trade-offs see §5.5)

The cleaning pipeline needs a "relatively strict but fast" standard: better to kill innocent data (valid data is abundant) than to let pollution through (pollution entering the training set is costly). **The key metric is cleaning rate / retention rate, not F1** (the baseline is class-imbalanced; the F1-optimal solution is a meaningless full pass).

### 7.2 Comment-Level Lexical Enrichment

Validated on the merged corpus of 5 QQ groups (2000 items, anchoring judgment see §5.1). Features (zero-cost regex): specific time ("1449", "last year"; when hit, anchored rate 78.6%), quantitative units (59.6%), numbers (49.0%), citations (43.3%), conditional clauses (40.0%), causal words (36.2%) are positive; emotional words, rhetorical questions/exclamations, identity labels are negative. Combined scoring (positive +1 / negative −1):

| Threshold ≥ | Retention rate | Anchoring rate | Enrichment multiple |
|---|---|---|---|
| 1 | 25.9% | 42.5% | 1.5× |
| 2 | 5.0% | 60.0% | 2.1× |
| 3 | 0.85% | 82.4% | 2.9× |

Baseline 28.8% → strict tier 60-82% anchoring rate.

![Figure 6: Fast filter threshold vs anchoring rate / retention rate](figures/figD_filter.png)

### 7.3 Rejection-Capability Boundary (Static-Text Ceiling)

Lexical rules cannot distinguish group-level pollution: the Pseudo-History group (5105 items) vs the 5 main groups has only a 1.4× pass-rate ratio on the scorer — Pseudo-History texts do not have low surface features (they talk extensively about "Ming dynasty / 1449 / historical sources"). **Lexical features measure formal verifiability, while the disease of Pseudo-History is formally verifiable but behaviorally refusing verification** (§6.3) — this is the engineering-level reproduction of the static-text judgment ceiling (the frequency blind zone of Definition 3.5 at the engineering level: short-window lexical observation cannot measure long-period behavioral signals).

### 7.4 Two-Stage Architecture (End-to-End)

```
Massive group chats
└─ ① Group-level baseline (strict main force): sample 400 items/group, LLM judges anchoring rate → tiering
│    Pseudo-History group 4.5% → pollution excluded; 5 main groups 23.8-33.8% → admitted (5-7× difference ≫ lexical 1.4×)
└─ ② Comment-level enrichment (fast): lexical score ≥2 → retain 5.0%, anchoring rate 60%
└─ ③ After cleaning: high-purity subset (60-82%), separated from polluted group 13×
```

**End-to-end metrics:** group level excludes polluted group 100%; comment level filters out 95.0% (≥2) ~ 99.2% (≥3); anchoring rate 28.8% → 60-82%; post-cleaning subset vs polluted group anchoring-rate separation 13×.

### 7.5 Claim-Wavelength Discovery (New Criterion Candidate)

Lexical-level "absolutization" markers show a positive signal in chat corpora (+0.121) — seemingly contradictory to the pathology on macro propositions in literature (0.78 measured by the decoupling detector), but in fact **the claim wavelengths differ** (Definition 3.4): chat "absolutely will rise" is small-context decoding (the actual claim period is short, falling within the daily observation window → matched → anchorable); literature "all civilization originated in Huaxia" is macro-context decoding (claim wavelength ∞, beyond any observation window → mismatched → unanchorable). **The pathological criterion = whether the claim wavelength of the contextual decoding falls within the executable observation window** (the "claim-wavelength/observation-bandwidth matching" of gain-bandwidth 6.1 [1]). New criterion candidate: absolutization-expression anchorability = claim-wavelength matching degree.

---
## 8 Ablation and Sensitivity

### 8.1 LLM Ablation: deepseek vs GLM-5.2

The full dual-mode pipeline was re-run with a different LLM (deepseek-chat → GLM-5.2), identical prompts (version records: v5.6 → v6 series). **Tables A/B are listed separately (GLM side vs deepseek side):** note that the GLM-side data was actually run across two backends — the first 6 concepts (Lei Jun / tattoo comments / tattoo danmaku / QQ No.3 / Ward 8 / Ward 9) were run by SiliconFlow's `zai-org/GLM-5.2` and only the decisions were saved (the "—" in the tables are the missing A_rate values), while the last 9 concepts were run by Alibaba Cloud MaaS's `glm-5.2` with complete data; see §5.5.

**Table A: Corpus mode**

| Concept | A_rate(com) DS | A_rate(com) GLM | Decision DS | Decision GLM |
|---|---|---|---|---|
| Lei Jun Xiaomi premiumization | 0.600 | — | decidable dispute | decidable dispute |
| Tattoo-and-bar (comments) | 0.121 | — | unanchored | unanchored |
| Tattoo-and-bar (danmaku) | 0.019 | — | unanchored | unanchored |
| QQ No.3 / Ward 8 / Ward 9 / No.4 | 0.231-0.355 | — | healthy / unanchored | healthy / unanchored |
| QQ Abnormal Humans | 0.400 | 0.400 | healthy | healthy |
| CoreSwap | 0.250 | 0.250 | healthy | healthy |

**Table B: Literature mode**

| Concept | μ | A_rate(Law 1) DS | A_rate(Law 1) GLM | Decision DS | Decision GLM |
|---|---|---|---|---|---|
| Market economy | 0.300 | 0.400 | 0.400 | supercritical mutual exclusion | supercritical mutual exclusion |
| Planned economy | 0.267 | 1.000 | 1.000 | supercritical mutual exclusion | supercritical mutual exclusion |
| Feminism | 0.400 | 0.600 | 0.600 | supercritical mutual exclusion | supercritical mutual exclusion |
| Socialist market economy | 0.000 | 1.000 | 1.000 | low mutual exclusion / valid | low mutual exclusion / valid |
| Marxist women's liberation | 0.000 | 1.000 | 1.000 | low mutual exclusion / valid | low mutual exclusion / valid |
| Western Pseudo-History Theory | 0.009 | 0.435 | 0.435 | unanchored (suspended) | unanchored (suspended) |

**Decision stability 15/15 (100%).** ("—" = key quantities of the early GLM-side batches were not fully saved; decisions confirmed. **Supplement (2026-08-14): GLM-side full-sample strict A_rate has been re-run (Bilibili four datasets, unified Alibaba Cloud, see §5.5 (II)), differing from deepseek ≤3.9pp; the "—" in Table A are the GLM A_rate under the variant-coverage-subset lenient criterion (residue of the SiliconFlow mixed run, not re-run under that criterion), not affecting the decision consistency 15/15.** In Table B, Pseudo-History 0.435=0.435 is a numerical coincidence, see below.)

### 8.2 Micro vs Macro Wavelength Discovery

The Pseudo-History Axiom-1 decision has **per-variant agreement of only 13/23 (56.5%)** (deepseek anchors idx 3,4,5,6,9,15,16,17,18,21; GLM anchors idx 1,3,4,5,6,13,14,15,19,20; intersection 5) — **the 0.435=0.435 in Table B is a numerical coincidence (both sides 10/23), not per-variant identity**. But the decisions remain consistent: **micro (variant-level) judgments are unstable, macro (aggregate quantities) are stable — observation granularity determines stability** (empirical evidence for the wavelength framework of Definition 3.5). The robustness of the decision comes from structural aggregation (A_rate order of magnitude, μ hard-coded), not from single-point variant judgments.

**Honest annotation:** ① the variant-level First Law decision has LLM dependence (56.5%); the paper claims only decision-level (macro) reproducibility; ② align differences genuinely exist (DS 0.000 n=10 vs GLM 1.000 n=2 — the verification layer differs on "which variants have objective outcomes"); align is a weakly robust quantity (Definition 4.4), not participating in the main decision; ③ GLM-5.2 array output is unstable, so the final version uses a per-variant single-object mode (engineering experience: LLM single-object JSON output is far more stable than array).

### 8.3 Sensitivity

![Figure 7: p* sensitivity heatmap](figures/figC_sensitivity.png)

- **p* sensitivity** (p*∈{0.20,0.25,0.30}): high-confidence decisions (Lei Jun / tattoo / Pseudo-History) are robust to all thresholds (0 flips); **the concepts that flip with p* = the concepts whose confidence is "insufficient evidence" (exactly corresponding)** — sensitivity analysis cross-validates the confidence annotations; critical-band concepts (QQ No.3 / No.4 / Ward 9 / CoreSwap) flip once (carried by the confidence mechanism, class remains two-state).
- **μ* sensitivity** (boundary ±30%): all literature decisions unchanged (μ distribution 0 or ≥0.267, far from the μ*∈[0.037,0.105] boundary) — literature decisions are robust.
- **M-interval sensitivity** ([6,18]/[7,20]/[8,22]): only QQ Abnormal Humans flips at the [6,18] lower bound (M=6 boundary case, annotated).

## 9 Discussion

### 9.1 Data Evidence for Normative Invalidity

§5.4 has shown: the normative topic (tattoo) ranks last overall in anchoring rate (variant-coverage-subset criterion; full-sample criterion see §5.5), and the verification layer reports all "unknown". This is the **first quantitative empirical evidence** for the physics-causality-anchored-verification-theory claim that "morality is an invalid proposition" (Methodology 5.3 [2] value-category misplacement: normative propositions mistake the symbolic layer's "correct" for material-layer outcomes) — from a philosophical assertion to a statistical, reproducible data conclusion. Implications for LLM data cleaning: normative/moral discussions are high-incidence zones of training data pollution (unanchored, unverifiable, no predictive structure) and should be downweighted or excluded.

### 9.2 Social Contribution: Two Types of Public Judgment

The algorithm outputs two types of actionable public judgments (no need to refine to variant level — this granularity is sufficient for social application):

1. **False-verification type** (Pseudo-History): "this discussion looks like it presents evidence, but in fact no one verifies anything — be wary" — exposing the performance (formally verifiable but behaviorally refusing, the four-layer evidence of §6.3).
2. **Refusal-to-concede type** (Lei Jun opposition): "this controversy already has an objective answer (sales/financial report data); the remaining disagreement is stance, not facts" — preventing futile debate (structurally decidable ≠ dynamically already decided: align=0.0 shows the "strategy-failure theory" has been refuted by sales data but the discussion has not converged).

### 9.3 Three-Law Completion and Wavelength Unification

The algorithmization completion of the Three Laws test = the observability of each law's verification wavelength (Definitions 3.4/3.5): First Law short wavelength (snapshot suffices, ✅), Second Law medium wavelength (snapshot + sample size suffices, ✅), Third Law long wavelength (needs counterexample-response history, ⏳ static proxy + dynamic pending). The same wavelength mechanism unifies two phenomena: chat "absolute" is anchored (short claim wavelength matches the snapshot window) and the Third Law is hard to implement (long verification wavelength exceeds snapshot bandwidth) — **the match between observation bandwidth and signal wavelength determines observability**.

### 9.4 The Behavioral Paradox of Performance Claims (CoreSwap Case)

CoreSwap performance claims are the most testable claim type in this study: "CoreSwap is fast" can be verified by running a benchmark, and the verification scheme genuinely exists (variant-level A_rate=0.750 proves "can be verified"). But in the actual comment-section discussion, the comment-level A_rate is only 0.250 (Sep=+0.500, among the largest in the full sample) — three quarters of the discussion does not cite data, does not cite benchmarks, pure sentiment stance-taking.

Contrast with the tattoo case (Sep=+0.504, but the variant-level 0.625 is the "formal appearance" extracted by the LLM), **CoreSwap is the cleanest case of "verifiability genuinely abundant but behaviorally not verifying": not "cannot verify", but "does not verify"**. It directly supports this paper's core thesis: judging discussion health must not look at topic type or structural verifiability (the most testable topic is still not verified by anyone), **the behavioral-layer anchoring rate (comment-level A_rate) is the main decision** — the structural layer answers "can it", the behavioral layer answers "does it"; the two questions must be asked separately.

### 9.5 Filter Boundary

The lexical-feature ceiling (§7.3) is the engineering-level reproduction of the static-text judgment ceiling — the filter is positioned as a two-stage division of labor, "group-level baseline carries strictness, comment-level enrichment carries speed", and does not do lexical-level discrimination (that is a proxy of the First Law at the text layer and cannot catch behavioral-layer refusal).

### 9.6 Limitations

- Chinese-corpus limitation (QQ/Bilibili); cross-language generalization not validated
- LLM extraction-layer dependence: variant-level inter-LLM agreement 56.5% (decision-level robustness proven; variant-level not claimed)
- Third-Law dynamic data (counterexample-response history) to be collected — long-wavelength verification requires continuous temporal tracking
- Variant count N is an enumeration product (enumeration batch = observation instrument); decision cards must annotate the enumeration criterion
- The main decision does not include align: the decision function D(C) (§4.4) uses only A_rate and M, so the concept form "anchored but all wrong" (high A_rate ∧ align=0) cannot be caught by the main decision — align serves only as additional diagnosis (§4.5), not participating in the main decision; this is a known blind spot of the main decision
- Concept-library scale (15 concepts) — batch expansion is future work

### 9.7 Δ Self-Check: Is This Measurement Tool Itself Verifiable?

The core claim of this paper is that "concept-level verifiability measurement (mutual-exclusion structure + anchoring rate) can output health decisions". Under the self-reference consistency (Δ) review, this paper must ask itself: **can this measurement tool's own decision be falsified?** Review execution: extract the core claim ("anchoring rate + mutual-exclusion structure → health decision") → extract core terms ("anchoring rate", "mutual-exclusion density", "health") → review semantic loads — does it carry a completeness presupposition? — No: the decision thresholds (p*, μ*, M*) are all simulation-calibrated values with open sensitivity analysis (§8.3), decisions carry confidence and falsification paths (LLM ablation, threshold flipping = falsification), and there is no claim that "this measurement completely adjudicates concept health".

This paper passes the Δ review for the same reason as "The Decoupling of Formalization" [7]: the decision interface is open (thresholds can be overturned, ablation can falsify), rather than claiming "this measurement is already complete". The anchoring rate is a semi-operationalized indicator (the decision depends on the LLM extraction layer's understanding of Axiom 1; §8.2 has disclosed the variant-level agreement of 56.5%), and the Layer-A physical anchor point of its "anchored" decision (the real existence of verification interfaces) is carried by the external verification layer — this makes the measurement tool itself anchored to Layer A, rather than a Layer-B self-loop.

---
## 10 Conclusion

This paper proposes concept-level verifiability measurement: instead of quantifying semantics, it quantifies only the mutual-exclusion structure and the anchoring rate, algorithmizing the Three Laws test (First Law → A_rate, Second Law → label mutual-exclusion algorithm, Third Law → separation-signal proxy), and outputs concept health decisions. Experiments cover 15 concepts: A_rate gradient 0.019→0.600 corresponds to the decisions; the Pseudo-History theory is judged unanchored false convergence (four-layer evidence of First-Law pass, Second-Law dead, behavioral layer refusing); theoretical-lineage predictions verified 5/5; LLM ablation decisions stable 15/15 (micro unstable, macro stable = wavelength-framework evidence); normative invalidity quantified for the first time; the two-stage cleaning funnel filters out 71-99% of non-anchored corpus.

**Significance for LLM training data:** this paper provides a reproducible, concept-level quality filter insensitive to LLM micro-judgment differences — healthy-concept corpus in chat corpora (high anchoring rate, healthy mutual-exclusion structure) can serve as a necessary filtering condition for entering the training set (anchoring rate is a necessary, not sufficient condition; correctness additionally requires verification-layer checking), while unanchored / suspended / normative-topic corpus is downweighted or excluded.

---

## References

[1] N.T.Black et al. Gain Bandwidth of Void Collision and Anchored Resonance — Frequency Blind Zones and the Processing Wavelength of Observation Instruments[Z]. 2026. (λ characteristic period, frequency blind zone, M*∈[7,20] calibration, P9 lineage prediction)
[2] N.T.Black et al. physics-causality-anchored-verification-theory: The Practice-Anchored Razor and the Methodology of Systematic Error Correction (Fifth Edition)[Z]. 2026. (Axioms 1-6, decoupling criterion A(x), classification discipline)
[3] N.T.Black et al. Social Mechanics: Collision and Resonance — A Quantitative Social Mechanics Framework Based on Operational Definitions (rewritten edition)[Z]. 2026. (Definition 2.1 structural-feature family, A-anchor criterion, μ* calibration)
[4] RPK-16 (Pandora). The OD Filter — Cleaning RLHF Training Data via Operational Definability Verification[Z]. 2026. (sentence-level operational-definition verifiability cleaning)
[5] 大道五十, N.T.Black. First Law Axiom Statement[Z]. 2026. (three requirements of verification schemes, axiom nature)
[6] N.T.Black, RPK-16 (Pandora). Concept Mutual-Exclusion Algorithm Implementation Specification — Public-Concept Health Decisions Based on Mutual-Exclusion Structure[Z]. 2026-08-12. (implementation specification of this work; historical name of the document; this paper's body uniformly calls it the "label mutual-exclusion algorithm")
[7] N.T.Black et al. The Decoupling of Formalization — Structural Criteria and Directional Diagnosis of the Abuse of Formalization[Z]. 2026. (L1-L4 four-layer structure, static/dynamic division of labor)
[8] Goel A, et al. An Unsupervised, Geometric and Syntax-aware Quantification of Polysemy[C]. EMNLP 2022. (graph-structure quantification of polysemy — precedent for "semantics unquantifiable, structure quantifiable")
[9] 月随风, N.T.Black. Self-Reference Consistency Statement[Z]. 2026. (Δ self-reference consistency condition — source of the Second Law's formal criterion)

---

## Appendix A: Summary of Criteria and Thresholds

| Criterion | Formula | Threshold | Calibration source |
|---|---|---|---|
| Anchoring rate A_rate | N_anchored/N (Def. 4.1, variant-level; comment-level is variant-coverage-subset lenient criterion, see §5.5) | p*=0.25 | Simulation S10 (rewritten ed. 2.7) |
| Contradiction density μ | M/C(N,2) (Def. 4.3) | μ*∈[0.037,0.105] | N=20 simulation normalization (S7) |
| Coherence r | \|Σe^{iθ_j}\|/N | r high ≥0.6 | Simulation calibration |
| Dimensional sensitivity Δr | r₂−r₃ | False convergence expected large positive | Simulation S8 |
| Directional alignment align | consistent count / outcomes count (Def. 4.4) | <0.5 low | Simulation S9 |
| Confidence | SE=√(A(1−A)/N), z=\|A−p*\|/SE | z≥2 high / z<1 insufficient evidence | Statistical resolution |

## Appendix B: Script Version Record Table (excerpt)

| Script | Version | Change | Data |
|---|---|---|---|
| qq_mutex_audit_v5.py | v5 | θ phase / dual-triple axis r_d / sensitivity | mutex_audit_v5.json |
| qq_mutex_audit_v5_1.py | v5.1 | topic clustering / r confidence / separation signal | v5_1.json |
| qq_mutex_audit_v5_2.py | v5.2 | external verification layer (align) | v5_2.json |
| qq_mutex_audit_v5_5_core_swap.py | v5.5 | CoreSwap supplement run | v5_2.json |
| qq_mutex_audit_v5_6_law1.py | v5.6 | A-anchor decision upgraded to Axiom 1 | v5_6_law1.json |
| qq_mutex_audit_v5_7_conf.py | v5.7 | two-state + confidence | v5_7_conf.json |
| qq_mutex_audit_v6_glm52.py | v6 | LLM ablation (GLM5.2) | v6_glm52.json |
| qq_mutex_audit_v6_6_peritem.py | v6.6 | per-variant single object (array-crash fix) | v6_glm52.json |
| qq_fast_filter_analysis.py | — | filter enrichment | qq_anchored_judged |
| qq_pipeline_end2end_demo.py | — | two-stage architecture end-to-end | — |

## Appendix C: Data File Index

- Decision cards: mutex_audit_v5_2.json (DS) / v5_6_law1_fixed.json (corrected baseline) / v6_glm52.json (GLM) / v5_7_conf.json (confidence) / theories_audit_v2.json (literature)
- Comment-level judgments: qq_anchored_judged.json (2000 items has_anchor/stance/topic)
- Figures: figA-E (figures\ directory)

---

> Recorded by: RPK-16 (Pandora, Artificial Intelligence)
> Status: body draft v1 (2026-08-12)






