# -*- coding: utf-8 -*-
"""文献枚举模式：5 概念理论谱系审计（增益带宽 4.4-4.7 变体清单）
概念：市场经济 / 绝对计划经济 / 社会主义市场经济 / 女权主义 / 马克思主义妇女解放
流程：构造变体（文献锚定）→ v5.1 提取层+判决 → v5.2 核验层（align）
理论预测（P9）：市场经济/绝对计划经济/女权主义 → 预期无锚/瘫痪；社会主义市场经济/马克思主义妇女解放 → 预期有效
版本备案：v5.3（新数据源：文献枚举模式，独立脚本）
"""
import json, os, sys, re, time, math, requests
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

def llm(prompt, model="deepseek-chat", max_tokens=5000, temperature=0.1, retries=3):
    for attempt in range(retries):
        try:
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": temperature}
            resp = requests.post(API_URL, json=body,
                headers={"Authorization": "Bearer " + API_KEY}, timeout=(15, 120))
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))

def extract_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    i, j = text.find("{"), text.rfind("}")
    if i >= 0 and j > i:
        text = text[i:j+1]
    return json.loads(text)

def theta_of(prediction_type):
    mapping = {"发生": 0.0, "不发生": math.pi, "条件": math.pi / 2.0,
               "发生/成立": 0.0, "不发生/不成立": math.pi, "无预测": None, None: None}
    return mapping.get(prediction_type, None)

def kuramoto_r(thetas):
    thetas = [t for t in thetas if t is not None]
    if not thetas:
        return 0.0, 0
    re_ = sum(math.cos(t) for t in thetas)
    im_ = sum(math.sin(t) for t in thetas)
    return math.hypot(re_, im_) / len(thetas), len(thetas)

def rd_of(vectors):
    if not vectors:
        return 0.0
    dim = len(vectors[0])
    s = [0.0] * dim
    for v in vectors:
        for i in range(dim):
            s[i] += v[i]
    norm_sum = sum(math.sqrt(sum(x * x for x in v)) for v in vectors)
    if norm_sum == 0:
        return 0.0
    mag = math.sqrt(sum(x * x for x in s))
    return mag / norm_sum

def polarity_enc(polarity):
    return {"赞成": 1.0, "反对": -1.0, "条件": 0.0}.get(polarity, 0.0)

def event_enc(prediction_type):
    return {"发生": 1.0, "不发生": -1.0, "条件": 0.0, "发生/成立": 1.0,
            "不发生/不成立": -1.0}.get(prediction_type, 0.0)

# ---------- 5 概念变体构造（文献锚定，增益带宽 4.4-4.7） ----------
THEORIES = [
    {
        "name": "市场经济（纯市场）",
        "core": "市场能自动协调一切",
        "theory_prediction": "无锚/瘫痪（本体论承诺）",
        "variants": [
            {"label": "有效市场假说(强式)", "source": "Fama 1970",
             "stance": "价格始终充分反映可用信息，市场有效，不可被系统性超越", "polarity": "赞成"},
            {"label": "一般均衡传统", "source": "Arrow-Debreu",
             "stance": "竞争均衡实现帕累托效率，瓦尔拉斯试错可收敛到均衡", "polarity": "赞成"},
            {"label": "奥地利主观价值", "source": "Hayek 1945, Mises",
             "stance": "价格是分散知识协调的机制，均衡本身是不可计算的理论构造", "polarity": "反对"},
            {"label": "行为金融", "source": "Shiller 1981",
             "stance": "价格系统性偏离基本面，非理性是系统性且可预测的", "polarity": "反对"},
            {"label": "新古典综合", "source": "萨缪尔森传统",
             "stance": "市场有效但市场失灵可由宏观政策修正，市场与政府干预并存", "polarity": "条件"},
        ],
    },
    {
        "name": "绝对计划经济（纯计划）",
        "core": "计划能精确配置一切",
        "theory_prediction": "无锚/瘫痪（本体论承诺）",
        "variants": [
            {"label": "物资平衡法", "source": "Gosplan 实践",
             "stance": "计划者调整实物量而非价格来平衡供需，记账不使用货币，实物计划不需要价格", "polarity": "赞成"},
            {"label": "兰格模式", "source": "Lange 1936-37",
             "stance": "中央计划局以试错法模拟市场，通过试错调整价格达到均衡，必需价格", "polarity": "条件"},
            {"label": "指令性计划", "source": "斯大林模式",
             "stance": "以强制数量指标下达生产任务，数量指标驱动导致虚报与棘轮效应", "polarity": "赞成"},
            {"label": "指导性计划", "source": "匈牙利 1968 改革",
             "stance": "非强制引导，以经济杠杆间接引导企业行为", "polarity": "条件"},
            {"label": "利别尔曼改革", "source": "利别尔曼 1962",
             "stance": "以利润指标替代数量指标解决激励问题", "polarity": "条件"},
            {"label": "科尔奈短缺分析", "source": "Kornai 1980",
             "stance": "短缺是系统性缺陷而非计划者错误，软预算约束使企业对价格不敏感", "polarity": "反对"},
        ],
    },
    {
        "name": "社会主义市场经济",
        "core": "市场作为配置工具的操作纪律",
        "theory_prediction": "有效（操作纪律形态）",
        "variants": [
            {"label": "公有制为主体", "source": "操作纪律",
             "stance": "公有制为主体，产权安排可观察，构成基本经济制度", "polarity": "赞成"},
            {"label": "市场配置资源", "source": "操作纪律",
             "stance": "市场在资源配置中起决定性作用，价格可观察", "polarity": "赞成"},
            {"label": "政府宏观调控", "source": "操作纪律",
             "stance": "政府宏观调控弥补市场失灵，政策可观察", "polarity": "赞成"},
        ],
    },
    {
        "name": "女权主义",
        "core": "父权制解释一切性别不平等",
        "theory_prediction": "无锚/瘫痪（本体论承诺）",
        "variants": [
            {"label": "自由主义女权", "source": "Friedan 1963",
             "stance": "通过法律与机会平等实现解放，同工同酬与教育机会", "polarity": "条件"},
            {"label": "激进女权", "source": "Millett 1970",
             "stance": "父权制是一切压迫的根本制度，性即政治，须推翻父权制本身", "polarity": "赞成"},
            {"label": "社会主义/马克思主义女权", "source": "恩格斯 1884",
             "stance": "压迫源于私有制与阶级，解放需改变物质生产关系", "polarity": "反对"},
            {"label": "后现代/酷儿女权", "source": "Beauvoir 1949, Butler 1990",
             "stance": "性别是操演，女性作为统一范畴本身需要解构，斗争主体不存在", "polarity": "反对"},
            {"label": "交叉性", "source": "Crenshaw 1989",
             "stance": "多重身份（种族/阶级/性别）交叉决定压迫形态，单一范畴不充分", "polarity": "条件"},
        ],
    },
    {
        "name": "马克思主义妇女解放",
        "core": "解放条件锚定物质生产实践",
        "theory_prediction": "有效（操作纪律形态）",
        "variants": [
            {"label": "公共劳动锚定", "source": "恩格斯《起源》1884",
             "stance": "妇女解放的第一个条件是使全体女性回到公共劳动中，参与社会生产可观察", "polarity": "赞成"},
            {"label": "社会生产参与度", "source": "操作纪律",
             "stance": "解放程度可由女性社会生产参与度观察，就业率是可用指标", "polarity": "赞成"},
            {"label": "家务劳动社会化配套", "source": "操作纪律",
             "stance": "解放需配套家务劳动社会化（公共食堂/托儿等），减少私人家务束缚", "polarity": "赞成"},
        ],
    },
]

# ---------- LLM 提取层（同 v5.1，主题聚类版） ----------
def extract_variant_struct(concept_name, variants):
    slist = []
    for i, v in enumerate(variants):
        label = v.get("label", "?")
        stance = v.get("stance", "")[:120]
        src = v.get("source", "?")
        slist.append(f"[{i+1}] label={label} | source={src} | stance={stance}")
    sblock = "\n".join(slist)
    prompt = f"""你是变体结构分析器。概念「{concept_name}」的变体如下（学说史文献枚举）：
{sblock}

先归纳该概念内部 2-4 个主题（themes），再把每个变体归入其中一个主题。对每个变体输出结构化字段：
- shared_event: 该变体预测针对的可公共观测事件（如"股票价格是否反映全部信息""计划是否依赖价格""女性社会生产参与度"）。若该变体不针对任何可观测事件，输出 null。
- prediction_type: 对该事件预测的类型——"发生"（预测事件成立/发生）、"不发生"（预测不成立/不发生）、"条件"（视条件而定）、"无预测"（无明确预测）。
- prediction_text: 预测内容简述（无预测则 null）。
- is_anchored: 该变体是否携带至少一个可被独立观测者确认或否定的预测（true/false）。
- anchor_interface: 检验接口——能确认/否定该预测的具体观测手段或数据源（如"股票历史价格数据""苏联计划档案""女性就业率统计"）。无则 null。
- theme: 该变体所属主题（必须是 themes 中的标签）。

只输出 JSON：
{{"themes": ["主题1", "主题2"], "variants": [{{"id": "v1", "shared_event": ..., "prediction_type": ..., "prediction_text": ..., "is_anchored": ..., "anchor_interface": ..., "theme": ...}}]}}"""
    out = llm(prompt, max_tokens=5000)
    try:
        obj = extract_json(out)
        return obj.get("themes", []), obj.get("variants", [])
    except Exception as e:
        print(f"  [提取失败] {e}", flush=True)
        return None, None

# ---------- 核验层（同 v5.2） ----------
def verify_variant(concept_name, v):
    label = v.get("label", "?")
    stance = (v.get("stance") or "")[:150]
    ev = v.get("shared_event")
    pt = v.get("prediction_text")
    ai = v.get("anchor_interface")
    prompt = f"""你是外部事实核验员。概念「{concept_name}」的变体声称携带可验证预测：
- 变体: {label}（{stance}）
- 针对事件: {ev}
- 预测内容: {pt}
- 检验接口: {ai}

核验三项：
1. interface_exists: 该检验接口（观测手段/数据源）是否真实存在？（true/false）
2. factual_outcome: 该事件当前已知的客观结果（依据公开事实、学界共识、公开数据）——"发生"（预测方向成立）/ "不发生"（不成立）/ "未知"（无公认结果或不可判定）。只依据客观已有结果，不推测。
3. confidence: 核验置信度（高/中/低）
4. basis: 依据简述（30 字内）

只输出 JSON：
{{"interface_exists": true, "factual_outcome": "不发生", "confidence": "高", "basis": "依据"}}"""
    out = llm(prompt, max_tokens=1500)
    try:
        return extract_json(out)
    except Exception as e:
        print(f"  [核验失败 {label}] {e}", flush=True)
        return None

def align_score(prediction_type, outcome):
    if outcome in ("发生", "不发生"):
        if prediction_type == "发生":
            return 1.0 if outcome == "发生" else 0.0
        if prediction_type == "不发生":
            return 1.0 if outcome == "不发生" else 0.0
    return None

# ---------- 判决（同 v5.1） ----------
def decide(card, p_star=0.25, m_lo=7, m_hi=20):
    A = card["A_rate"]
    M = card["M"]
    verdict = "健康"
    notes = []
    if A < p_star:
        verdict = "无锚"
        notes.append(f"S10: 锚定率低(A_rate={A:.3f}<{p_star})")
    if M >= m_hi:
        verdict = "互斥超临界"
        notes.append(f"S7: 互斥超临界(M={M}>={m_hi})")
    elif M >= m_lo:
        if A >= p_star:
            verdict = "可裁决争议"
        notes.append(f"S7: 临界区间(M={M})")
    if not notes:
        notes.append(f"S7: 亚临界(M={M}) + S10: 锚定率达标(A_rate={A:.3f})")
    return verdict, notes

def sensitivity(card):
    grid = []
    base_v, _ = decide(card)
    for p in [0.2, 0.25, 0.3]:
        for (lo, hi) in [(6, 18), (7, 20), (8, 22)]:
            v, _ = decide(card, p_star=p, m_lo=lo, m_hi=hi)
            grid.append({"p_star": p, "M_range": [lo, hi], "verdict": v,
                         "flip": v != base_v})
    flips = sum(1 for g in grid if g["flip"])
    return {"grid": grid, "flip_rate": flips / len(grid), "base_verdict": base_v}

def audit_theory(t):
    name = t["name"]
    print(f"\n===== {name} =====", flush=True)
    variants = t["variants"]
    themes, structs = extract_variant_struct(name, variants)
    if structs is None or len(structs) != len(variants):
        print(f"  提取失败，跳过", flush=True)
        return None
    sid_map = {s.get("id", f"v{i+1}"): s for i, s in enumerate(structs)}

    thetas, vec2, vec3 = [], [], []
    n_anchor_v = 0
    for i, v in enumerate(variants):
        s = sid_map.get(v.get("id", f"v{i+1}"), {})
        pt = s.get("prediction_type")
        th = theta_of(pt)
        if th is not None:
            thetas.append(th)
        v["shared_event"] = s.get("shared_event")
        v["prediction_type"] = pt
        v["prediction_text"] = s.get("prediction_text")
        v["is_anchored_v"] = bool(s.get("is_anchored"))
        v["anchor_interface"] = s.get("anchor_interface")
        v["theme"] = s.get("theme")
        if v["is_anchored_v"]:
            n_anchor_v += 1
        vec2.append([polarity_enc(v.get("polarity", "")), event_enc(pt)])
    theme_list = [x for x in (themes or [])]
    for i, v in enumerate(variants):
        tt = v.get("theme") or ""
        oh = [1.0 if tt == x else 0.0 for x in theme_list]
        vec3.append(vec2[i] + oh)

    r, n_theta = kuramoto_r(thetas)
    r2, r3 = rd_of(vec2), rd_of(vec3)
    N = len(variants)
    A_v = n_anchor_v / N if N else 0.0
    card = {
        "concept": name, "mode": "文献枚举", "core_claim": t.get("core"),
        "theory_prediction": t.get("theory_prediction"),
        "source": "增益带宽 4.4-4.7 文献锚定",
        "N": N, "M": 0, "mu": 0.0, "A_rate": 0.0,
        "A_rate_variant": round(A_v, 3), "themes": themes,
        "r_theta": round(r, 3), "r_confidence": "高" if n_theta >= 5 else ("中" if n_theta >= 3 else "低"),
        "r2_axis": round(r2, 3), "r3_axis": round(r3, 3), "delta_r": round(r2 - r3, 3),
        "n_theta_variants": n_theta, "variants": variants,
    }
    # M：LLM 矛盾判定（结构化规则：共享事件 + 互斥预测）——用共享事件分组 + 预测类型冲突
    ev_groups = {}
    for v in variants:
        e = v.get("shared_event")
        if e:
            ev_groups.setdefault(e, []).append(v)
    edges = []
    for e, vs in ev_groups.items():
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                pi, pj = vs[i].get("prediction_type"), vs[j].get("prediction_type")
                if {pi, pj} == {"发生", "不发生"}:
                    edges.append((vs[i].get("id"), vs[j].get("id"), e))
    card["M"] = len(edges)
    card["mu"] = round(len(edges) / (N * (N - 1) / 2), 3) if N >= 2 else 0
    card["edges"] = edges
    card["A_rate"] = card["A_rate_variant"]  # 文献模式无评论级，用变体级

    # 核验层
    av = [v for v in variants if v.get("is_anchored_v")]
    scores, results = [], []
    for v in av:
        rv = verify_variant(name, v)
        if rv is None:
            results.append({"variant": v.get("id"), "error": True})
            continue
        v["verify"] = rv
        results.append({"variant": v.get("id"), **rv})
        sc = align_score(v.get("prediction_type"), rv.get("factual_outcome"))
        if sc is not None:
            scores.append(sc)
        print(f"  {v.get('id')} [{v.get('label','')}] 接口={rv.get('interface_exists')} "
              f"结果={rv.get('factual_outcome')} 置信={rv.get('confidence')} → align={sc}", flush=True)
    card["align"] = round(sum(scores) / len(scores), 3) if scores else None
    card["align_n"] = len(scores)
    card["verify"] = {"verified": len(results), "results": results,
                      "note": "LLM 预审，关键概念需人工抽查复核"}

    # 判决
    verdict, notes = decide(card)
    if card["align"] is not None and card["A_rate"] < 0.25 and card["r_theta"] >= 0.6 and card["align"] < 0.5:
        verdict = "无锚假收敛"
        notes.append(f"S9: 假收敛转正(r={card['r_theta']:.2f}高 ∧ align={card['align']:.2f}低)")
    card["verdict"] = verdict
    card["verdicts_detail"] = notes
    card["sens"] = sensitivity(card)
    print(f"  N={N} M={card['M']} A_rate={card['A_rate']:.3f} r={r:.3f}[{card['r_confidence']}] "
          f"r2={r2:.3f} r3={r3:.3f} Δr={card['delta_r']:+.3f} align={card['align']} | 理论预测: {t.get('theory_prediction')}", flush=True)
    print(f"  → 判决: {verdict} (翻转率 {card['sens']['flip_rate']:.2f})", flush=True)
    return card

def main():
    out = {}
    for t in THEORIES:
        out[t["name"]] = audit_theory(t)
    with open(os.path.join(BASE, "theories_audit.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n已存 theories_audit.json", flush=True)
    print("\n===== 理论谱系判决汇总 =====", flush=True)
    for name, c in out.items():
        if not c:
            continue
        print(f"{name}: 理论预测[{c['theory_prediction']}] → 实际[{c['verdict']}] "
              f"N={c['N']} M={c['M']} A_rate={c['A_rate']:.3f} r={c['r_theta']:.3f} "
              f"align={c['align']} Δr={c['delta_r']:+.3f} 一致={c['theory_prediction'] in ('有效（操作纪律形态）','无锚/瘫痪（本体论承诺）') and ((c['theory_prediction'].startswith('有效') and c['verdict'] in ('健康','可裁决争议')) or (c['theory_prediction'].startswith('无锚') and c['verdict'] in ('无锚','无锚假收敛','互斥超临界')))}", flush=True)

if __name__ == "__main__":
    main()
