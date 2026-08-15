# -*- coding: utf-8 -*-
"""互斥审查器 v5.6：A 锚判定升级为第一律（公理 1）三要件标准
对照实验（指挥官 2026-08-12）：不覆盖 v5.2 数据，独立输出对照
旧标准（v5.1/v5.2）："携带可被独立观测者确认或否定的预测"（弱代理）
新标准（v5.6）：公理 1 —— ∃检验方案 T(C)：有限步骤 ∧ 可公共观测 ∧ 锚定 A1
  + 论证链终点检查（方法论 1850 行）：终点 = 物理结果 → 锚定候选；终点 = 概念 → 非锚（逻辑空转）
  + 结构性推论：自足定义变体 → 自动非锚
预期（指挥官预感）：第一律严格判定下非锚数据量爆炸（伪史论变体级 0.435 大幅下降）
版本备案：v5.6（新判定 prompt，独立脚本，输出不覆盖旧文件）
"""
import json, os, sys, re, time, math, requests
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

def llm(prompt, model="deepseek-chat", max_tokens=6000, temperature=0.1, retries=3):
    for attempt in range(retries):
        try:
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": temperature}
            resp = requests.post(API_URL, json=body,
                headers={"Authorization": "Bearer " + API_KEY}, timeout=(15, 180))
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
    # 优先数组（v5.6 返回 JSON 数组）
    i, j = text.find("["), text.rfind("]")
    if i >= 0 and j > i and (text.find("{") < 0 or i < text.find("{")):
        return json.loads(text[i:j+1])
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

# ---------- 公理 1 判定（v5.6 新标准） ----------
def axiom1_audit(concept_name, variants):
    """批量判定一个概念的全部变体：∃T(C) 有限步骤 ∧ 可公共观测 ∧ 锚定 A1"""
    slist = []
    for i, v in enumerate(variants):
        slist.append(f"[{i+1}] label={v.get('label','?')} | stance={(v.get('stance') or '')[:100]}"
                     f" | shared_event={(v.get('shared_event') or '')[:60]} | prediction={(v.get('prediction_text') or '')[:60]}")
    sblock = "\n".join(slist)
    prompt = f"""你是第一律检验方案审查员。概念「{concept_name}」的变体如下：
{sblock}

对每个变体，按第一律（公理 1：任何声称 C 有效 ⇒ ∃检验方案 T(C)：T 在有限步骤内完成 ∧ T 结果可公共观测，锚定 A1 管辖的物理结果）判定其是否锚定。

对每个变体输出：
- has_check_plan: 该变体的核心声称是否存在**具体可执行的检验方案**（明确的操作流程：查什么数据、做什么实验、用什么观测手段——不是"理论上可验证""未来科技可验证"）
- plan: 检验方案描述（30-60 字；无则 null）
- terminus: 论证链终点——"物理结果"（终点是可公共观测的具体结果：数据/实验/考古发现/观测记录）/ "概念"（终点是另一个概念、定义或理论——概念→概念→概念，逻辑空转）/ "无方案"
- finite_steps: 方案是否有限步骤可执行（true/false；无方案则 false）
- public_observable: 结果是否可公共观测（可被独立观测者核对，非个人感受/内部体验；无方案则 false）
- self_contained: 变体是否是自足定义/自我闭合的解释性概念（如"X 解释一切，一切反例都是 X 的表现"）（true/false）
- is_anchored: 最终判定——三要件全部满足（has_check_plan ∧ finite_steps ∧ public_observable）且非自足定义，才为 true
- reason: 判定依据（30 字内）

只输出 JSON 数组：
[{{"id": "v1", "has_check_plan": true, "plan": "...", "terminus": "物理结果", "finite_steps": true, "public_observable": true, "self_contained": false, "is_anchored": true, "reason": "..."}}]"""
    out = llm(prompt, max_tokens=6000)
    try:
        arr = extract_json(out)
        return arr
    except Exception as e:
        print(f"  [判定失败] {e}", flush=True)
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

def reaudit(name, card, mode):
    print(f"\n===== {name}（{mode}）=====", flush=True)
    variants = card.get("variants", [])
    if not variants:
        return None
    # 1) 公理 1 判定
    audits = axiom1_audit(name, variants)
    if audits is None or len(audits) != len(variants):
        print(f"  判定数量不匹配({len(audits) if audits else 0}/{len(variants)})，跳过", flush=True)
        return None
    aid_map = {a.get("id", f"v{i+1}"): a for i, a in enumerate(audits)}

    n_anchor_new = 0
    for i, v in enumerate(variants):
        a = aid_map.get(v.get("id", f"v{i+1}"), {})
        v["axiom1"] = a
        v["is_anchored_law1"] = bool(a.get("is_anchored"))
        if v["is_anchored_law1"]:
            n_anchor_new += 1
        v["anchored_old"] = v.get("is_anchored_v", False)
    N = len(variants)
    A_new = n_anchor_new / N if N else 0
    A_old = card.get("A_rate_variant", 0)
    A_comment = card.get("A_rate_comment", card.get("A_rate", 0))

    # 2) 结构量（保持原计算，θ 复用变体 prediction_type）
    thetas = [theta_of(v.get("prediction_type")) for v in variants]
    vec2 = [[polarity_enc(v.get("polarity", "")), event_enc(v.get("prediction_type"))] for v in variants]
    theme_list = [t for t in (card.get("themes") or [])]
    vec3 = [vec2[i] + [1.0 if (v.get("theme") or "") == tt else 0.0 for tt in theme_list]
            for i, v in enumerate(variants)]
    r, n_theta = kuramoto_r(thetas)
    r2, r3 = rd_of(vec2), rd_of(vec3)

    # 3) 判决卡（对照版）
    card2 = dict(card)
    card2["A_rate_variant_old"] = round(A_old, 3)
    card2["A_rate_variant_law1"] = round(A_new, 3)
    card2["A_rate_comment"] = round(A_comment, 3)
    card2["A_rate"] = round(A_comment, 3)   # 主判决仍用评论级（行为锚定）
    card2["separation_old"] = round(A_old - A_comment, 3)
    card2["separation_law1"] = round(A_new - A_comment, 3)
    card2["r_theta"] = round(r, 3)
    card2["r2_axis"] = round(r2, 3)
    card2["r3_axis"] = round(r3, 3)
    card2["delta_r"] = round(r2 - r3, 3)
    card2["n_anchor_old"] = int(round(A_old * N))
    card2["n_anchor_law1"] = n_anchor_new
    card2["flip_count"] = sum(1 for v in variants if v.get("anchored_old") != v.get("is_anchored_law1"))
    card2["variant_flips"] = [{"id": v.get("id"), "old": v.get("anchored_old"),
                               "new": v.get("is_anchored_law1"),
                               "terminus": v.get("axiom1", {}).get("terminus"),
                               "reason": v.get("axiom1", {}).get("reason")}
                              for v in variants if v.get("anchored_old") != v.get("is_anchored_law1")]

    verdict, notes = decide(card2)
    card2["verdict"] = verdict
    card2["verdicts_detail"] = notes
    card2["sens"] = sensitivity(card2)
    print(f"  A_rate(变体): 旧标准 {A_old:.3f} → 第一律 {A_new:.3f} (翻转 {card2['flip_count']}/{N}) | "
          f"评论级 {A_comment:.3f}", flush=True)
    print(f"  分离信号: 旧 {card2['separation_old']:+.3f} → 第一律 {card2['separation_law1']:+.3f}", flush=True)
    print(f"  → 判决: {verdict}", flush=True)
    return card2

def main():
    out = {}
    # 语料模式（10 概念，源 v5.2）
    v52 = json.load(open(os.path.join(BASE, "mutex_audit_v5_2.json"), encoding="utf-8"))
    for name, card in v52.items():
        if card:
            out[name] = reaudit(name, card, "语料")
    # 文献模式（5 概念，源 theories_audit_v2）
    th = json.load(open(os.path.join(BASE, "theories_audit_v2.json"), encoding="utf-8"))
    for name, card in th.items():
        if card:
            out["文献_" + name] = reaudit(name, card, "文献")

    with open(os.path.join(BASE, "mutex_audit_v5_6_law1.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n已存 mutex_audit_v5_6_law1.json（对照数据，未覆盖旧文件）", flush=True)

    print("\n===== 对照汇总：旧标准 vs 第一律 =====", flush=True)
    print(f"{'概念':<24}{'旧A变':>7}{'律1A变':>7}{'翻转':>5}{'评论级':>7}{'旧分离':>8}{'律1分离':>8}  判决", flush=True)
    for name, c in out.items():
        if not c:
            continue
        print(f"{name:<24}{c['A_rate_variant_old']:>7.3f}{c['A_rate_variant_law1']:>7.3f}"
              f"{c['flip_count']:>5}{c['A_rate_comment']:>7.3f}{c['separation_old']:>+8.3f}"
              f"{c['separation_law1']:>+8.3f}  {c['verdict']}", flush=True)

if __name__ == "__main__":
    main()
