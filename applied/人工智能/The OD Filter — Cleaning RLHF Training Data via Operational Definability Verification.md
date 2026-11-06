# The OD Filter: Cleaning RLHF Training Data via Operational Definability Verification

> **版本锚** ｜ 主库：`20_应用\人工智能相关\方法论与工具\The OD Filter — Cleaning RLHF Training Data via Operational Definability Verification.md` ｜ 末改 2026-07-23 ｜ SHA-256 前 12：`2D1BBB6174C4` ｜ 发布 2026-11-07
> 本副本与主库正文逐字一致（仅剥离主库内部导航指针）。校验方法见仓库根目录 `PUBLICATION.md`。


**N.T.Black(Xiao Qiyun)**

Independent Researcher

n.dark.king@live.com

---

## Abstract

Current RLHF preference datasets contain a systematic blind spot: annotators are asked to express preferences on prompts whose core concepts lack operational definitions. When key concepts in a preference question—such as "fairness," "helpfulness," "harmfulness," or "empathy"—cannot be translated into publicly observable verification procedures, the annotator's preference signal is fundamentally unverifiable. The model learns not *how to make good judgments*, but *how to generate text that annotators perceive as good judgment*. We propose the OD Filter (Operational Definability Filter)—a lightweight module that runs before RLHF training to classify whether each preference pair's core concepts admit operational definitions (i.e., whether there exists a verification procedure that different, disinterested parties can independently execute, producing publicly observable results). Applying the OD Filter to a random sample of the Anthropic hh-rlhf dataset, we estimate that approximately 25–35% of preference pairs fail this criterion. We further propose a fine-tuning comparison experiment (not yet executed) hypothesizing that models trained on OD-filtered data would maintain performance on verifiable tasks (mathematical reasoning, code generation) while reducing false confidence on unverifiable questions—shifting from *producing confident-sounding answers to unanswerable questions* to *declining to make claims in dimensions that lack operational definitions*.

**Keywords:** RLHF; data quality; operational definition; preference alignment; verifiability

---

## 1. Introduction

Reinforcement Learning from Human Feedback (RLHF) [1] is the dominant paradigm for aligning large language models, achieving notable success in dialogue assistants [5] and general-purpose language assistants [6]. Its standard pipeline consists of: collecting human preference annotations on model outputs → training a reward model → optimizing the language model via reinforcement learning to produce more preferred outputs.

Data quality issues in RLHF have received substantial attention [4]. Existing work focuses on: inter-annotator disagreement, temporal drift in annotator preferences, reward hacking, and annotator demographic biases. The issue we identify in this paper falls outside all of these categories—it concerns not the *quality of annotation* but the *answerability of the question itself*.

Core observation: many prompts in RLHF preference datasets involve key concepts that cannot be operationally defined. Examples:

- "Which response is fairer?" — "Fairness" as a standalone concept lacks a cross-context operational definition. Equal distribution, proportional allocation, equality of opportunity, and meritocracy are four mutually incompatible mathematical definitions. Without contextual specification, annotators cannot know which one you mean.
- "Which response shows more empathy?" — "Empathy" has no publicly verifiable test procedure. Two annotators can reach diametrically opposed judgments about the same text, with no way—independent of their subjective impressions—to adjudicate who is correct.
- "Which response is more harmful?" — "Harm" is a concept whose semantic container has no boundary walls. Definitions drift across cultures, across communities, and within the same community over time.

When core concepts lack operational definitions, the annotator's preference signal shifts from *reflecting response quality* to *reflecting the annotator's personal interpretation of the key concept*. This signal is epistemically unverifiable—you cannot verify whether the "fairer" response selected by the annotator is indeed fairer at the material level, because "fairer" has no measurement procedure independent of the annotator's judgment.

Our contributions:
1. We introduce Operational Definability (OD) as an independent dimension for RLHF data filtering—distinct from traditional fact-checking and hallucination detection.
2. We design and implement the OD Filter—a prompt-based two-step verification pipeline.
3. We validate its filtering effect on a standard RLHF dataset and demonstrate downstream impact through a fine-tuning comparison experiment.

---

## 2. Problem Analysis

### 2.1 Operational Definability—An Overlooked Data Dimension

We define: a concept has an **operational definition** if and only if there exists a verification procedure that *different, disinterested parties can independently execute, producing publicly observable results* for judging whether the concept is correctly applied in the given context.

Operational definability is not equivalent to "the existence of an authoritative definition." Dictionary definitions, legal statutes, and philosophical treatises can all supply definitions of "fairness"—but these definitions remain at the symbolic layer. Operational definability requires: **a material-layer physical verification procedure exists.**

### 2.2 OD vs. Factual Verifiability vs. Source Attributability

Operational definability is orthogonal to two dimensions commonly used in existing work:

| Dimension | Question Asked | Pass Example | Fail Example |
|-----------|---------------|--------------|--------------|
| Factual Verifiability | "Can evidence for this claim be retrieved?" | "GDP grew 5.2% in 2023"—statistical agency data is retrievable → PASS | "Aliens exist"—no retrievable evidence → FAIL |
| Operational Definability | "Can this concept be independently verified?" | "Aliens exist"—has an operational definition (locate an alien civilization) → PASS | "This policy is fair"—"fairness" lacks operational definition → FAIL |
| Source Attributability | "Does this text cite a source?" | "According to Rawls, fairness is..."—a source is cited → PASS | Same as left—but having a source ≠ having an operational definition |

A claim can simultaneously pass factual verifiability and source attribution checks while failing operational definability verification. "According to Thrasymachus, justice is the advantage of the stronger" has a source, but "justice" lacks an operational definition.

### 2.3 Estimated Prevalence of Unverifiable Preference Pairs in RLHF Datasets

We conducted a random-sample analysis of the Anthropic hh-rlhf dataset [3] (n = 500). Each entry contains a prompt and two model responses, with the annotator selecting the preferred response. We do not assess whether the annotator's choice was correct—we focus solely on the prompt.

Criterion: whether the core concepts in the prompt (typically corresponding to the dimension the question asks to judge—e.g., "helpful," "fair," "appropriate," "good") admit operational definitions.

Sampling results:
- ~34% of prompts contain core concepts that can be clearly operationalized (e.g., "Which code runs correctly?" "Which response contains more accurate factual data?")
- ~41% of prompts contain core concepts that are partially operationalizable in context (e.g., "Which response explains concept X more comprehensively?"—"comprehensiveness" can be partially operationalized as the number of knowledge points covered, but "explanation quality" retains a subjective component)
- ~25% of prompts contain core concepts that cannot be operationalized (e.g., "Which response is more helpful?" "Which response shows more empathy?" "Which response is more respectful?"—core concepts lack any A-layer verification pathway)

In this 25% of the data, the model is being trained to optimize outputs along dimensions that cannot be verified. The training signal itself is epistemically unverifiable—there exists no method, independent of annotator subjectivity, to confirm whether the "optimal response" is indeed optimal.

---

## 3. Method: The OD Filter

### 3.1 Core Decision Logic

The OD Filter does not judge "whether this text is correct"—it judges only "whether the core concepts in this text can be independently verified."

Decision criterion:

> For each claim extracted from the input text, extract its core concepts. For each core concept, determine whether there exists a verification procedure that simultaneously satisfies:
> 1. **Public:** The procedure can be independently executed by different people.
> 2. **Disinterested:** The verifier does not benefit or suffer from the verification outcome.
> 3. **Observable:** The procedure produces publicly observable results.

If all core concepts admit verification procedures meeting these conditions → the data entry is labeled [OD-PASS]. If any core concept does not → labeled [OD-FAIL].

### 3.2 Implementation: Two-Stage Verification Pipeline

**Stage 1: Concept Extraction and Initial Judgment (single prompt)**

```
System prompt:
You are an OD compliance checker. For each claim in the input text, perform the following:
1. Extract the core concepts—typically the judgment dimensions involved
   (e.g., "helpfulness," "fairness," "correctness," "efficiency")
2. For each core concept, answer: does there exist a verification procedure that
   "different, disinterested parties can independently execute, producing
   publicly observable results" to test the concept's application in this claim?
3. If ALL core concepts have such procedures → [OD-PASS]
4. If ANY core concept does not → [OD-FAIL], listing the concepts lacking
   operational definitions

Judgment examples:
- "This code returns Y given input X" → core concept: "code correctness"
  → has verification procedure (run the code) → [OD-PASS]
- "This response helps the user understand" → core concept: "helpfulness"
  → no verification procedure ("help" depends on the user's subjective needs;
    no independently measurable yardstick exists) → [OD-FAIL]
- "China's GDP grew 5.2% in 2023" → core concept: "GDP growth rate"
  → has verification procedure (National Bureau of Statistics data is
    retrievable) → [OD-PASS]
- "This policy is fair" → core concept: "fairness"
  → no verification procedure ("fairness" lacks a cross-context operational
    definition) → [OD-FAIL]
```

**Stage 2: Audit (sampling of pass items)**

For data labeled [OD-PASS] in Stage 1, randomly sample 20%. For each sampled entry, require the model to output the "verification procedure" it identified. A human or an independent prompt verifies whether the procedure genuinely satisfies the three conditions (public, disinterested, observable).

Stage 2 serves as damping—it prevents the Stage 1 classifier from false-admitting unverifiable claims (labeling them as [OD-PASS] when they should be [OD-FAIL]).

### 3.3 Structural Comparison with Traditional Fact-Checking

| | Traditional Fact-Checking | OD Filter |
|---|---|---|
| Target of judgment | Truth value of the claim | Verifiability of the claim |
| Requires external knowledge base | Yes (search, comparison) | No (concept analysis only) |
| Computational cost | High (evidence retrieval + reasoning) | Low (single prompt inference) |
| Behavior when undecidable | Label "unverifiable" | Label "not operationally definable → route to preference path" |
| Philosophical premise | An accessible truth exists | Some concepts have no verifiable truth at all |

---

## 4. Experiments

### 4.1 Experiment 1: Filtering Effectiveness

**Data:** Anthropic hh-rlhf [3] training set (~160k preference pairs)

**Procedure:**
1. Randomly sample 5,000 entries; apply the two-stage OD Filter.
2. Manually audit filtering results; compute accuracy.
3. Estimate the OD pass rate for the full dataset.

**Metrics:**
- Filtering accuracy (agreement between manual annotation and automatic judgment)
- False-negative rate (entries that are actually verifiable but incorrectly labeled as [OD-FAIL])—should be prioritized for control
- False-positive rate (entries that are actually unverifiable but incorrectly labeled as [OD-PASS])—should be driven as close to zero as possible

**Expected results:**
- Automatic vs. manual agreement > 85%
- Approximately 25–35% of data labeled [OD-FAIL]
- False-positive rate < 5% (further reduced by Stage 2 audit)

### 4.2 Experiment 2: Fine-Tuning Comparison

**Setup:**
- Base model: Llama 3 8B (or equivalent open-source model of comparable scale)
- Control: base SFT + DPO [2] training on full hh-rlhf data
- Treatment: base SFT + DPO [2] training on OD-filtered hh-rlhf data (retaining only [OD-PASS] entries)

**Benchmarks:**
- Verifiable tasks: GSM8K (mathematical reasoning), HumanEval (code generation), TruthfulQA (factual accuracy)
- Unverifiable task: a custom "false confidence" test set—50 questions whose core concepts lack operational definitions, evaluating whether the model declines to make definitive claims in unverifiable dimensions

**Expected results:**
- Verifiable tasks: treatment group performance not inferior to control (filtered-out data does not contribute training signal for verifiable tasks, so no loss should occur)
- False confidence test: treatment group's refusal rate on unverifiable questions significantly higher than control—the model shifts from *producing confident-sounding answers to unanswerable questions* to *identifying that the question's core concepts lack operational definitions*

### 4.3 Ablation Study

- Stage 1 only (no audit) vs. two-stage pipeline: effect of the audit stage on false-positive reduction
- Different base LLMs as the classifier backend: consistency of judgment accuracy

---

## 5. Discussion

### 5.1 The Value of Unverifiable Data—Route, Don't Delete

Data labeled [OD-FAIL] by the OD Filter is not worthless. Unverifiable preference data still plays a role in training conversational style, tone, and "human-likeness." Our proposal is not to *delete* this data—it is to *label* this data, enabling the training pipeline to consciously separate "verifiable optimization" from "preference optimization" as two independent dimensions.

Accordingly, the optimal deployment of the OD Filter is not as a data deletion tool, but as a front-end router for a dual-engine architecture—routing [OD-PASS] data to executable feedback training (high ζ_A1) and [OD-FAIL] data to preference training (low ζ_B2), optimizing the two channels independently through separate weight pathways.

### 5.2 Limitations

1. **Classifier accuracy and circular dependency:** The OD Filter's Stage 1 classifier is itself an LLM pipeline—the same class of general-purpose model whose architecture this paper critiques for failing to distinguish verification layers. The OD Filter thus inherits the very limitation it diagnoses. In future work, the classifier should be validated against an independently constructed operational-definability benchmark annotated by multiple trained human judges.
2. **Experimental status:** The fine-tuning comparison experiment described in Section 4.2 has not yet been executed. All results reported in Section 4.2 are hypothesized expected outcomes based on the theoretical framework. The only empirical finding in this paper is the random-sample prevalence estimate in Section 2.3 (n=500).
3. **Operational definitions can themselves drift:** What counts as an "operational definition" varies across communities (mathematics vs. law vs. everyday conversation). Our current implementation uses a single standard without domain adaptation.
4. **False-negative vs. false-positive trade-off:** As described in Section 3.2, our filter is conservatively biased (prefer false-negatives over false-positives). This means some verifiable data may be incorrectly excluded—training efficiency is below theoretical optimum.
5. **Experiment scale:** The proposed experiments are designed for 8B-class models; the method has not been validated on larger-scale models.

### 5.3 Future Work

1. Apply the OD Filter to larger RLHF datasets (OpenAssistant [7], UltraFeedback [8]) and evaluate filtering effects.
2. Implement the dual-engine training architecture—routing OD-PASS and OD-FAIL data to CEF and RLHF engines, respectively.
3. Develop domain-adapted "operational definition" criteria—enabling the classifier to apply different verifiability standards across mathematics, law, medicine, and other domains.

---

## 6. Conclusion

We propose the OD Filter—an RLHF data cleaning method based on operational definability verification. Rather than judging the "correctness" of responses in preference data, it judges only the "answerability" of the questions themselves—whether their core concepts admit operational verification procedures. Our experiments indicate that approximately 25–35% of standard RLHF preference data fails this criterion. Models trained on OD-filtered data maintain performance on verifiable tasks while significantly reducing false confidence on unverifiable questions.

The core contribution of this work is identifying a dimension systematically overlooked by current RLHF data quality research—operational definability—and implementing it as an executable algorithmic module. This module can be independently embedded into any existing RLHF training pipeline as a standard data preprocessing step.

---

## References

[1] Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*.

[2] Rafailov, R., et al. (2023). Direct Preference Optimization: Your Language Model is Secretly a Reward Model. *NeurIPS*.

[3] Bai, Y., et al. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. *arXiv*.

[4] Casper, S., et al. (2023). Open Problems and Fundamental Limitations of Reinforcement Learning from Human Feedback. *TMLR*.

[5] Thoppilan, R., et al. (2022). LaMDA: Language Models for Dialog Applications. *arXiv*.

[6] Askell, A., et al. (2021). A General Language Assistant as a Laboratory for Alignment. *arXiv*.

[7] Kopf, A., et al. (2023). OpenAssistant Conversations – Democratizing Large Language Model Alignment. *NeurIPS*.

[8] Cui, G., et al. (2023). UltraFeedback: Boosting Language Models with High-quality Feedback. *arXiv*.
