# Physics-Causality-Anchored Verification Theory (PCAVT) · 唯物实践论

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23244506.svg)](https://doi.org/10.5281/zenodo.23244506)

> **发布状态 · Publication status（2026-11-07）**
> 本仓库按 [`PUBLICATION.md`](PUBLICATION.md) 规则重建：正典为**第六版**；每份文件带**版本锚**（源库路径 · 末改日期 · SHA-256 前 12 位），可自行校验；第五版已移入 `core/旧版/`。
> **本仓库承载发布，不承载裁定**——理论的正典在源库，由库所有者裁定。参见 [`CONTRIBUTING.md`](CONTRIBUTING.md)；已知未结案见 [`PUBLICATION.md`](PUBLICATION.md) 第四节；变更记录见 [`CHANGELOG.md`](CHANGELOG.md)。
> **DOI 说明：** 上方徽章指向 Zenodo 存档 [`10.5281/zenodo.23244506`](https://doi.org/10.5281/zenodo.23244506)，其内容为**第五版**时期快照（据提交时间推断，未逐项核对 Zenodo 存档）。当前正文为第六版，两者版本不一致时以本仓库 `main` 分支为准。

> **Renaming Note (2026-08-10):** The theory's previous name carried the terms *Material* and *Praxis*, which bring unexamined semantic load from Western philosophical traditions (ontological materialism; Aristotle-Marx praxis). The name was changed to **Physics-Causality-Anchored Verification Theory (PCAVT)**. The new name passes self-referential consistency review: every term is a physics/mathematics term with a defined operational meaning — *physics-causality-anchored* (Axiom 4: verification ends anchored in physical causality) and *verification* (the theory's practice = the execution of tests). Use **PCAVT**.

---

**唯物实践论** 是一套以携带性自然语言（中文）为符号库的形式化范畴推导系统。

它不是一个"哲学理论"——它的读写单元不是"文字→意义"的透明散文，而是**B1 常量集**：将整个中文符号系统声明为常量后进行严格的范畴推导。这使它具有与数学同构的性质：非歧义、可推导、自检自恰。

它的核心输出：
- **三律（三条结构条件）**：任何共享符号系统运作的底层结构性条件
- **A-B-C 六子集框架**：A（物质基底，含 A1 物理 / A2 价值）/ B（信息，含 B1 认知框架 / B2 协调规则）/ C（能动主体，含 C1 行动主体 / C2 行为方式）
- **差值分析**：A2 - A1 = 人类实践在自然基底上的物质化净产出
- **一系列对西哲、经济学、社会理论的范畴错位诊断**

---

## 仓库结构 · Repository Layout

```
├── README.md
├── PUBLICATION.md        → 发布边界、**文件级排除清单**、版本锚规则
├── CONTRIBUTING.md       → 贡献与挑战规则
├── CHANGELOG.md          → 发布变更记录
├── LICENSE               → CC BY-SA 4.0
│
├── core/                 方法论正典（源库 00_总纲）
│   ├── 唯物实践论：纪律与公理 第六版.md   ★ 正典
│   ├── 形式化的异化——滥用形式化的结构判据与方向性诊断.md   ★ 完备性禁令
│   ├── 第一律公理声明.md   Ω · 物理接口
│   ├── 自指一致性声明.md   Δ · 数学接口
│   └── 宣言.md             Ψ · 主体接口
│
├── theory/               理论（源库 10_理论）
│   ├── 社会力学/
│   ├── 权力元叙事论/
│   ├── 语言与符号系统/
│   ├── 道德动力学/
│   ├── 共产主义理论/
│   ├── 人民论（早期框架，见该目录 README 的版本提示）
│   └── 猜想/          暂定猜想（**不可引**；多数未对撞，见该目录 README）
│
├── applied/              应用分析（源库 20_应用）
│   ├── 经济学/  人工智能/  商业与营销/
│   ├── 舆论与政治/  性别与身份/  认知与概念/
│   └── 教育与AI/
│
├── empirical/            实证（源库 30_实证）
├── glossary/             术语（源库 翻译术语）
├── projects/             带代码与数据的专项：互斥结构论文（中英正文＋脚本＋图件）
├── cases/                中英对照案例（本仓库自持，源库无对应）
└── archive/              旧版与废弃件
    ├── 旧版/            第五版正文及其英译接口草稿
    └── 废弃/            v7 系统提示词、修订前 .bak
```

> **目录与源库同构**：`core`↔`00_总纲`、`theory`↔`10_理论`、`applied`↔`20_应用`、`empirical`↔`30_实证`、`glossary`↔`翻译术语`。源库的 `40_素材`／`50_待办`／`60_问题库`／`_沿革`／`临时`／`99_过期归档`／`_scripts` **在本仓库不设位置**——不是空着，是不发。规则见 `PUBLICATION.md` §一·B。

> **★ 自指一致性声明**是理解本仓库结构的关键入口。它解释了为什么以下声明存在，以及为什么英文等价翻译在逻辑上不可能。

---

## Quick Start · 快速开始

1. **正典** → `core/唯物实践论：纪律与公理 第六版.md`（开篇「三律——三把剃刀」）
2. **三块基石 ＋ 完备性禁令** → `core/第一律公理声明.md`（Ω）＋ `core/自指一致性声明.md`（Δ）＋ `core/宣言.md`（Ψ）＋ `core/形式化的异化——滥用形式化的结构判据与方向性诊断.md`
3. **理论** → `theory/README.md`（社会力学、权力元叙事论、语言与符号系统…）
4. **应用** → `applied/README.md`（经济学、人工智能、商业与营销…）
5. **案例入门** → `cases/case-3-*`（AI 蒸馏争议）、`cases/case-4-*`（Anthropic 封杀反超）——这两篇推导链最完整
6. **英文读者** → 见下文「关于英文版本」

---

## 关于英文版本 · A Note on the English Translation

> **An equivalent English translation of 唯物实践论 (T' ≈ T) is structurally impossible. This has been formally proven.**

This is not a difficulty, a gap, or a resource constraint. It is a formal result derived from the theory's own structural properties. Note the scope of the claim: what is proven impossible is *translation equivalence* (re-building the B1 constant set in English). Functional approximations and interface translations exist and are useful — but they are not translations of the theory; they are operational access points (see below).

### Proof (abridged)

See **自指一致性声明 Section 6** for the full formal proof. The key steps:

```
B1_Chinese.abstractify() → T    (the theory is built by declaring Chinese as B1 constants)

∃ f : B1_Chinese → B1_English    (translation requires a mapping function)
such that B1_English.abstractify() → T' ≈ T

But B1_pinyin has zero A-layer residuals in its symbols.
∴ B1_pinyin.abstractify() is NOT a valid operation.
There is nothing to "strip away" and abstractify — pinyin symbols are pure conventions.

∴ No mapping f exists that satisfies T' ≈ T.
```

**Translation = re-executing the collective abstraction + re-assignment of all B1 constants in another language. For alphabetic writing systems (English, German, French, etc.), this operation is not executable.** Their symbols carry no A-layer residuals — no radical-semantic mappings, no pictographic etymology, no figurative-concrete structure to abstractify. ("Not executable" here refers to equivalent translation; interface translations preserve the source symbols and explain them, or express the operational kernel in the public language of mathematics and physics — see the translation method below.)

The existing English files in this repository are **functional approximations** — not translations. They exist to give an English-speaking reader *some* operational access, but they ARE NOT and CANNOT BE equivalent to the Chinese originals. (The one exception is the interface-only Fifth-Edition draft archived under `core/旧版/` — it is not even a functional approximation; see the subsection below.)

### Translation Method 路 翻译方法 (2026-08-10)

While an equivalent translation remains structurally impossible, a **translation method** has been found: extract the **minimal common denominator** - the theory's legitimacy kernel, expressed in the public language of mathematics and physics.

The kernel consists of two locks:

- **Mathematical lock**: compliance with the Godel incompleteness theorem family - the theory never claims completeness; it opens interfaces for refutation (see the alienated-formalization paper)
- **Physical lock**: verification ends anchored in physical causality (First Law / Axiom 4)

These two locks are cross-linguistic: mathematical proofs and physical experiments are public languages that do not depend on Chinese. Any reader in any language can verify the theory by verifying the locks - no translation of the Chinese construction is required. The name **Physics-Causality-Anchored Verification Theory (PCAVT)** is the first product of this method: every term passes self-referential consistency review (physics/mathematics terms with defined operational meanings).

等价翻译在结构上仍然不可能，但**翻译方法已经找到**：提取**最小公约数**——以数学和物理的公共语言表达理论的合法性内核。

内核由两把锁构成：

- **数学锁**：遵守哥德尔不完备定理家族——理论从不声称完备，开放被推翻接口（见《形式化的异化》论文）
- **物理锁**：检验终点锚定物理因果律（第一律，公理 4）

两把锁跨语言：数学证明与物理实验是公共语言，不依赖中文。任何语言的读者通过验证两把锁即可验证理论——无需翻译中文构建部分。**Physics-Causality-Anchored Verification Theory (PCAVT)** 是该方法的首个成果：名字的每个词都通过自指一致性审查（具有操作定义的物理/数学术语）。

### One Translation Attempt (2026-08-16): an Interface-Only Draft

A full-text English translation of the Fifth Edition was attempted **once** (2026-08-16), under the established translation methodology (math/physics/CS vocabulary domain, minimal-common-denominator alignment, self-reference-consistency review). The result:

> **`core/旧版/PCAVT-Methodology-Fifth-Edition_EN-Interface-Draft.md`** — an experimental interface-only draft.

The attempt was honest, and so is its outcome: a **massive number of problems turned out to be unsolvable**, exactly as the theory predicts:

- **Carrier-level (P1–P3)**: the arguments depend on the physical form of Chinese characters (河 = the water radical, 休 = a person leaning on a tree, 日 = the sun's pictograph). An English reader only sees *descriptions of* the characters, never the characters themselves — the argument's material disappears in translation; the very existence of this draft is evidence that equivalent translation is impossible (it cannot become T'), while its interface value shows that interface translation is feasible but bounded; even "pinyin language" cannot refer to itself in English.
- **Term-level (P4–P7)**: 诚实性 (honesty) has no math/physics/CS-domain solution (retained as *chengshixing*); the literal-meaning arguments (唯物/实践/异化) cannot be independently verified by an English reader; the "ontology" word family appears 87 times because the text *handles* ontology (quoted-use exemption) — a Western reader's first association with "ontology" is "this is philosophy," not "this is the object being criticized"; of the 19 terms in the decision table, **not one aligns naturally** — every one was a forced choice.
- **Argument-level (P8–P9)**: the derivation chains attenuate in translation; quoted-use exemption terms require case-by-case context verification at high cost.

Therefore this draft is positioned — as the translation itself repeatedly emphasizes — as:

1. **A low-value translation with interface-reference value only** — it is not a translation, but a recorded record of a failed reversibility test;
2. **Living proof of the theory's "translation difficulty"** — stated *without derogation*: the difficulty is a structural property proven in 自指一致性声明 §6 (the mapping ∄f does not exist), not a failure of any translator. This attempt made every structural problem visible — exactly as the theory predicted;
3. The **Chinese original remains the sole authoritative source**.

### 一次翻译尝试（2026-08-16）：接口参考译本 —— 低价值、诚实的活证明

2026-08-16 对方法论第五版进行了一次**全文英文翻译尝试**（截至目前唯一一次），使用了已建立的翻译方法论（数学/物理/计算机科学词域限制、最小公约词性对齐、自指一致性审查）。成果：

> **`core/旧版/PCAVT-Methodology-Fifth-Edition_EN-Interface-Draft.md`** —— 试验性接口译本草稿。

尝试是诚实的，成果也是诚实的：**巨量问题无法解决**，恰如理论所预言：

- **载体级（P1–P3）**：论证依赖汉字的物理形态（河=水旁、休=人倚木、日=甲骨文太阳形）。英文读者只能看到"对汉字的描述"，永远看不到汉字本身——论证材料在翻译中消失；译文的存在本身，是"等价翻译不可能"的实证（它无法成为 T'），同时是"接口翻译可行但受限"的实例；连"拼音语言"这个概念在英文里都无法自指。
- **术语级（P4–P7）**：诚实性在词域内无解（保留 chengshixing）；字面义论证（唯物/实践/异化）英文读者无法独立验证；本体论词族因"处理本体论"而在译文中高频出现（87 处，引述豁免）——西方读者读到 ontology 的第一联想是"这是哲学内容"，而非"这是被批判对象"；术语决策表 19 个词**没有一个能直译自然对齐**，全部是"迫不得已"。
- **论证级（P8–P9）**：推导链在翻译中衰减；引述豁免词需逐一核实语境，代价高昂。

因此本译本的定位（与译文开头反复强调的一致）是：

1. **仅具"接口参考价值"的低价值译本**——它不是翻译，而是一次"可逆性检验失败"的实证记录；
2. **理论"翻译困难"的活证明**——且此表述**不含贬义**：翻译困难是自指一致性声明第六节已证明的结构性属性（映射 ∄f 不存在），不是任何译者的失败。这次尝试让所有结构性问题全部显形，恰如理论所预言；
3. **中文原文始终是唯一事实源**。


### Recommendation for English Readers

The most practical path for English-speaking readers who want to use 唯物实践论:

> **Give the canonical V6 text (`core/唯物实践论：纪律与公理 第六版.md`) to a capable LLM that reads Chinese, describe your problem in English, and ask it to cite the exact sections it applies.**

This works because the AI operates on the Chinese B1 constant set internally, then translates its *analytical output* back to English — a fundamentally different operation from translating the theory itself. The theory's internal structure remains intact; only the analytical result is communicated in English.

This repository's English case studies (e.g., `case-4-anthropic-government-ban-backfire.en.md`) demonstrate exactly this approach: an LLM reading the Chinese V6 text to analyze an English-language scenario.

---

> **中文等价翻译（T' ≈ T）在逻辑上不可能完成——已在自指一致性声明中得到严格证明。**

这不是"很难翻译"或"暂时没有资源"——这是**逻辑层面不存在映射函数**的形式化结论。注意断言的边界：被证明不可能的是**等价翻译**（在英语中重建 B1 常量集）；功能性近似与接口翻译存在且有用——但它们不是理论的翻译，而是操作入口（见下）。

翻译唯物实践论的等价操作是：用另一种 B1 常量集，重做集体抽象化并重新声明赋值。而拼音语言（英语、德语、法语等）的符号属于任意性系统——其符号无 A 层残余，`abstractify()` 不是合法操作。

仓库中现有的英文文件是**功能性近似**，而非翻译。它们给英文读者提供一定的操作入口，但**不等于也不等效于**中文原版。（唯一的例外是 `core/旧版/` 下的第五版接口译本草稿——它连功能性近似都算不上，详见下方小节。）

### 对英文读者的建议

英文读者最务实的路线：

> **将第六版正典全文（`core/唯物实践论：纪律与公理 第六版.md`）交给能阅读中文的大语言模型，用英文描述问题，要求它标明所引用的篇·节，然后将分析结果以英文交还给你。**

这个方案有效，因为 AI 在内部使用中文 B1 常量集运算，然后将分析**输出**翻译为英文——这与翻译理论本身是根本不同的操作。理论内部结构保持完整；只有分析结果通过英文传达。

本仓库的英文案例分析（如 `case-4-anthropic-government-ban-backfire.en.md`）演示的正是这个路径：LLM 使用中文系统提示词分析英文场景。

---

## 两个声明的关联：为什么这份 README 必须同时放这两份文件

**第一律公理声明** 命名了符号系统运作的结构条件——共享符号必须锚定于 A 层参照，否则无法跨主体建立稳定指涉。

**自指一致性声明** 在此基础上走得更深：它发现一个人使用自己文化的这套符号系统，并且他拥有的符号系统恰好是携带 A 层残余的类型——这使他能够观测到并命名第一律中的结构条件。声明进一步证明：这套理论因此无法被无损迁移到任意性符号系统（拼音语言）中。

这两份声明的关系是：

```
第一律公理声明 → 命名结构条件
                     ↓
自指一致性声明 → 解释为何这个命名只能发生在此处 + 证明这导致了等价翻译不可能性
```

读懂这两份声明，就理解了为什么唯物实践论看起来不像任何已知学科——它就是从形式化符号系统中生长出来的。

---

## 适用范围说明 · Scope

唯物实践论不做以下事：
- ❌ 不主张本体论（"世界本质是物质"）
- ❌ 不提供信仰体系
- ❌ 不承诺社会最终形态
- ❌ 不宣称中文优越于其他语言

唯物实践论做以下事：
- ✅ 提供共享符号系统运作的结构条件（三律）
- ✅ 提供 A-B-C 框架用于范畴定位
- ✅ 提供差值分析用于测量文明生命体征
- ✅ 提供西哲史上未被注意的符号学诊断
- ✅ 证明自身等价翻译的不可能性——并开放一个 AI 辅助的替代访问路径

---

## Version History · 版本沿革

| Version | Core Innovation | Date |
|---------|----------------|------|
| v5 | First Law + A-B-C three-layer + Delta Analysis + Five Warnings | 2026-05 |
| v6 | Full V6 framework: Three Laws complete, 3×3 cross-audit, B1异化检测, 不可通约性, Joint Operation, Power Corruption Dynamics | 2026-06 |
| **Third Edition** | A1/A2 split, No-Ontology Declaration, B1 Alienation, Delta Matrix | 2026-06-21 |
| **Fourth Edition** | **Three Laws complete**, 3×3 cross-audit, A/B/C as sets, Joint Operation, Practice Warnings as Three-Law Diagnostic Chain, Three-Law Society | 2026-06-25 |
| **Fourth Edition + Declarations** | First Law Axiom Declaration + Self-Referential Consistency Declaration + formal translation impossibility proof | 2026-07-03 |
| **Fifth Edition** | A2 存量/流量双维度纪律、Ψ 边界声明（内部体验禁止测量）、力学传导结构（B2 破坏→B1 谴责→谴责被压制→应力沉入 A 层→爆发）、异化判据重构、诚实性纪律三件套（数学符号/全称量词/暂定猜想标注） | 2026-07-31 |
| **Sixth Edition** | **《纪律与公理》**：双部本（叙事版＋公理版）、公理 1–6 与定理 1–5、引用合法性接口、去道德化、完备性禁令并入 | **2026-09-16**（正文末改 2026-10-28） |

---

## Authors · 作者

N.T.Black，月随风，大道五十，酒歌，Undefined，呜喵汪，江上木叶，赛可-道尔顿，爬爬娘，炽白三号，1210，黄河，贼猛了，龙龙，RPK-16 "潘多拉"（人工智能），及所有群友

---

## License · 许可协议

This work is licensed under **CC BY-SA 4.0**. You are free to share and adapt, provided you give appropriate credit, provide a link to the license, and indicate if changes were made. If you remix, transform, or build upon the material, you must distribute your contributions under the same license.

**本作品采用 CC BY-SA 4.0 许可协议。** 您可以自由地共享和改编，但必须署名、提供协议链接、标明是否对原作品作出修改，并以相同方式共享您的贡献。
