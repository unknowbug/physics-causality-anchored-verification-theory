# -*- coding: utf-8 -*-
"""CoreSwap 补跑：v5.1 提取 + v5.2 核验（指挥官抓漏：v5 系列只读了 mutex_audit_v4.json，丢了 v1 里的 CoreSwap）
版本备案：v5.5（CoreSwap 补跑，复用 v5.1/v5.2 逻辑）
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

# ---------- 从 v1 构造 CoreSwap 变体（direction → polarity） ----------
def build_core_swap_variants(v1_card):
    vs = []
    labels = {
        "v1": "玩梗嘲讽派", "v2": "技术支持派", "v3": "中立观望派", "v4": "实证质疑派",
        "v5": "一致性质疑派", "v6": "AI代码质疑派", "v7": "性能否定派", "v8": "缺陷指出派",
    }
    for v in v1_card["variants"]:
        d = v.get("direction", 0)
        pol = "赞成" if d == 1 else ("反对" if d == -1 else "条件")
        vs.append({
            "id": v["id"], "label": labels.get(v["id"], v["id"]),
            "polarity": pol, "stance": v.get("stance", ""),
            "source": "B站评论",
        })
    return vs

# ---------- 提取层（v5.1 版） ----------
def extract_variant_struct(concept_name, variants):
    slist = []
    for i, v in enumerate(variants):
        slist.append(f"[{i+1}] label={v.get('label')} | polarity={v.get('polarity')} | stance={v.get('stance','')[:120]}")
    sblock = "\n".join(slist)
    prompt = f"""你是变体结构分析器。概念「{concept_name}」的变体如下：
{sblock}

先归纳该概念内部 2-4 个主题（themes），再把每个变体归入其中一个主题。对每个变体输出结构化字段：
- shared_event: 该变体预测针对的可公共观测事件。若该变体不针对任何可观测事件，输出 null。
- prediction_type: "发生"/"不发生"/"条件"/"无预测"。
- prediction_text: 预测内容简述（无预测则 null）。
- is_anchored: 该变体是否携带至少一个可被独立观测者确认或否定的预测（true/false）。
- anchor_interface: 检验接口描述。无则 null。
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

# ---------- 核验层（v5.2 版） ----------
def verify_variant(concept_name, v):
    label = v.get("label", "?")
    stance = (v.get("stance") or "")[:150]
    prompt = f"""你是外部事实核验员。概念「{concept_name}」的变体声称携带可验证预测：
- 变体: {label}（{stance}）
- 针对事件: {v.get('shared_event')}
- 预测内容: {v.get('prediction_text')}
- 检验接口: {v.get('anchor_interface')}

核验三项：
1. interface_exists: 该检验接口是否真实存在？（true/false）
2. factual_outcome: 该事件当前已知的客观结果——"发生"/"不发生"/"未知"。只依据客观已有结果，不推测。
3. confidence: 高/中/低
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
            grid.append({"p_star": p, "M_range": [lo, hi], "verdict": v, "flip": v != base_v})
    flips = sum(1 for g in grid if g["flip"])
    return {"grid": grid, "flip_rate": flips / len(grid), "base_verdict": base_v}

def main():
    v1 = json.load(open(os.path.join(BASE, "mutex_audit_v1.json"), encoding="utf-8"))
    cs = v1["CoreSwap性能声称"]
    variants = build_core_swap_variants(cs)
    name = "CoreSwap性能声称"
    print(f"===== {name} 补跑 =====", flush=True)
    themes, structs = extract_variant_struct(name, variants)
    if structs is None or len(structs) != len(variants):
        print("提取失败", flush=True)
        return
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
        "concept": name, "mode": "语料统计", "source": "B站 CoreSwap 视频评论（569 条）",
        "comments": 569, "N": N, "M": cs.get("M", 4), "mu": cs.get("mu", 0.143),
        "A_rate_comment": cs.get("A_rate", 0.25),
        "A_rate_variant": round(A_v, 3),
        "A_rate": round(cs.get("A_rate", 0.25), 3),
        "separation_signal": round(A_v - cs.get("A_rate", 0.25), 3),
        "r_theta": round(r, 3), "r_confidence": "高" if n_theta >= 5 else ("中" if n_theta >= 3 else "低"),
        "r2_axis": round(r2, 3), "r3_axis": round(r3, 3), "delta_r": round(r2 - r3, 3),
        "n_theta_variants": n_theta, "themes": themes,
        "align": "pending", "variants": variants,
    }
    verdict, notes = decide(card)
    card["verdict"] = verdict
    card["verdicts_detail"] = notes
    card["sens"] = sensitivity(card)
    print(f"  N={N} M={card['M']} μ={card['mu']:.3f} A_rate(评论)={card['A_rate_comment']:.3f} "
          f"A_rate(变体)={A_v:.3f} 分离={card['separation_signal']:+.3f} r={r:.3f}[{card['r_confidence']}] "
          f"r2={r2:.3f} r3={r3:.3f} Δr={card['delta_r']:+.3f}", flush=True)
    print(f"  → 判决: {verdict} (翻转率 {card['sens']['flip_rate']:.2f})", flush=True)

    # 核验
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
        print(f"  {v.get('id')} [{v.get('label','')}] 结果={rv.get('factual_outcome')} → align={sc}", flush=True)
    card["align"] = round(sum(scores) / len(scores), 3) if scores else None
    card["align_n"] = len(scores)
    card["verify"] = {"verified": len(results), "results": results}

    # 合并进 v5_2 判决卡
    v52 = json.load(open(os.path.join(BASE, "mutex_audit_v5_2.json"), encoding="utf-8"))
    v52[name] = card
    with open(os.path.join(BASE, "mutex_audit_v5_2.json"), "w", encoding="utf-8") as f:
        json.dump(v52, f, ensure_ascii=False, indent=2)
    print(f"\n已并入 mutex_audit_v5_2.json（{name}）", flush=True)

if __name__ == "__main__":
    main()
