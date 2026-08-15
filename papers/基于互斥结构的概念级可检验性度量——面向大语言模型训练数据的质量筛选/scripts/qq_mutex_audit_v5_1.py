# -*- coding: utf-8 -*-
"""互斥审查器 v5.1：修正 v5 首跑暴露的 3 个问题
v5.1 相对 v5 的调整（提示词 + 输出结构变更，版本备案）：
1. 主题轴改聚类：prompt 要求先归纳 2-4 个主题，变体归入（修复 v5 每变体一主题 → one-hot 正交稀释）
2. r 置信度标注：n_theta < 3 低置信 / 3-4 中 / >=5 高（修复 θ 覆盖率低时 r 极端值误读）
3. 分离诊断字段：separation_signal = A_rate_variant(变体级,形式可检验性) - A_rate_comment(评论级,行为锚定)
   ——伪史论 0.435 vs 0.045 的差距是"表演检验盲区"量化信号；主判决仍用评论级
v5 的 θ 相位映射 / 双三轴 r_d / 敏感性分析逻辑不变
"""
import json, os, sys, re, time, math, requests
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

def llm(prompt, model="deepseek-chat", max_tokens=4000, temperature=0.1, retries=3):
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

# ---------- 相位映射（确定性，不进 LLM） ----------
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

# ---------- LLM 提取层 v5.1：主题聚类版 ----------
def extract_variant_struct(concept_name, variants):
    slist = []
    for i, v in enumerate(variants):
        label = v.get("label", "?")
        stance = v.get("stance", "")[:120]
        pol = v.get("polarity", v.get("type", "?"))
        slist.append(f"[{i+1}] label={label} | polarity={pol} | stance={stance}")
    sblock = "\n".join(slist)
    prompt = f"""你是变体结构分析器。概念「{concept_name}」的变体如下：
{sblock}

先归纳该概念内部 2-4 个主题（themes），再把每个变体归入其中一个主题。对每个变体输出结构化字段：
- shared_event: 该变体预测针对的可公共观测事件（如"土木堡之变发生地""小米季度营收"）。若该变体不针对任何可观测事件，输出 null。
- prediction_type: 对该事件预测的类型——"发生"（预测事件成立/发生）、"不发生"（预测不成立/不发生）、"条件"（视条件而定）、"无预测"（无明确预测）。
- prediction_text: 预测内容简述（无预测则 null）。
- is_anchored: 该变体是否携带至少一个可被独立观测者确认或否定的预测（true/false）。
- anchor_interface: 检验接口——能确认/否定该预测的具体观测手段或数据源（如"碳十四测年""财报营收数据""考古遗址发掘"）。无则 null。
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

# ---------- 判决函数 D(C)（模拟阈值先行） ----------
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

# ---------- 主流程 ----------
def upgrade_card(name, card):
    print(f"\n===== {name} =====", flush=True)
    variants = card.get("variants", [])
    if not variants:
        print("  无变体，跳过", flush=True)
        return None

    themes, structs = extract_variant_struct(name, variants)
    if structs is None or len(structs) != len(variants):
        print(f"  提取结果数量不匹配({len(structs) if structs else 0}/{len(variants)})，跳过", flush=True)
        return None
    sid_map = {s.get("id", f"v{i+1}"): s for i, s in enumerate(structs)}
    card["themes"] = themes or []

    thetas = []
    vec2 = []
    vec3 = []
    n_anchor_v = 0
    for i, v in enumerate(variants):
        sid = v.get("id", f"v{i+1}")
        s = sid_map.get(sid, {})
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
        pe = polarity_enc(v.get("polarity", ""))
        ee = event_enc(pt)
        vec2.append([pe, ee])
    theme_list = [t for t in (themes or [])]
    for i, v in enumerate(variants):
        t = v.get("theme") or ""
        oh = [1.0 if t == tt else 0.0 for tt in theme_list]
        vec3.append(vec2[i] + oh)

    r, n_theta = kuramoto_r(thetas)
    r2 = rd_of(vec2)
    r3 = rd_of(vec3)
    delta_r = r2 - r3
    N = len(variants)
    A_v = n_anchor_v / N if N else 0.0

    card["N"] = N
    card["A_rate_comment"] = card.get("A_rate", 0.0)   # 评论级（行为锚定）→ 主判决
    card["A_rate_variant"] = round(A_v, 3)             # 变体级（形式可检验性外观）
    card["A_rate"] = round(card["A_rate_comment"], 3)
    card["separation_signal"] = round(A_v - card["A_rate_comment"], 3)  # 表演检验嫌疑信号
    card["r_theta"] = round(r, 3)
    card["r_confidence"] = "高" if n_theta >= 5 else ("中" if n_theta >= 3 else "低")
    card["r2_axis"] = round(r2, 3)
    card["r3_axis"] = round(r3, 3)
    card["delta_r"] = round(delta_r, 3)
    card["n_theta_variants"] = n_theta
    card["N_anchored_variant"] = n_anchor_v
    card["N_free_variant"] = N - n_anchor_v
    card["align"] = "pending(需外部核验)"

    verdict, notes = decide(card)
    card["verdict"] = verdict
    card["verdicts_detail"] = notes
    card["sens"] = sensitivity(card)

    print(f"  N={N} M={card['M']} A_rate(评论)={card['A_rate_comment']:.3f} A_rate(变体)={A_v:.3f} "
          f"分离信号={card['separation_signal']:+.3f} r(θ)={r:.3f}[{card['r_confidence']}] "
          f"r2={r2:.3f} r3={r3:.3f} Δr={delta_r:+.3f} themes={len(themes)}", flush=True)
    print(f"  → 判决: {verdict} | 敏感性翻转率: {card['sens']['flip_rate']:.2f}", flush=True)
    return card

def main():
    out = {}
    v4 = json.load(open(os.path.join(BASE, "mutex_audit_v4.json"), encoding="utf-8"))
    for name, card in v4.items():
        out[name] = upgrade_card(name, card)
    qq = json.load(open(os.path.join(BASE, "qq_anchor_mutex_v1.json"), encoding="utf-8"))
    for name, card in qq.items():
        out["QQ_" + name] = upgrade_card("QQ群:" + name, card)
    ph = json.load(open(os.path.join(BASE, "pseudohistory_variants.json"), encoding="utf-8"))
    ph_variants = ph.get("variants", [])
    ph_card = {
        "concept": "西方伪史论", "mode": "文献枚举", "source": "军事历史群 67 条关键词上下文",
        "comments": ph.get("hits", 60), "N": len(ph_variants), "M": 2, "mu": 0.009,
        "A_rate": 0.045, "variants": ph_variants,
    }
    out["西方伪史论(文献枚举)"] = upgrade_card("西方伪史论(文献枚举)", ph_card)

    with open(os.path.join(BASE, "mutex_audit_v5_1.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n已存 mutex_audit_v5_1.json", flush=True)

    print("\n===== 判决汇总(v5.1) =====", flush=True)
    for name, c in out.items():
        if c is None:
            continue
        print(f"{name}: N={c['N']} M={c['M']} A_rate={c['A_rate']:.3f} "
              f"变体级={c['A_rate_variant']:.3f} 分离={c['separation_signal']:+.3f} "
              f"r={c['r_theta']:.3f}[{c['r_confidence']}] Δr={c['delta_r']:+.3f} "
              f"→ {c['verdict']} (翻转率 {c['sens']['flip_rate']:.2f})", flush=True)

if __name__ == "__main__":
    main()
