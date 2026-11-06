# -*- coding: utf-8 -*-
"""互斥审查器 v6.2：GLM5.2 消融续跑——阿里云（DashScope 兼容端点）
版本备案：v6.2（换 API 源：SiliconFlow → 阿里云 MaaS；模型 glm-5.2）
断点续跑：读 mutex_audit_v6_glm52_partial.json（SiliconFlow 已完成 6 概念），跑剩余 9 个
每完成一个概念立即写输出（断点保护）
输出：mutex_audit_v6_glm52.json（完整对照，不覆盖 v5 系列）
"""
import json, os, sys, re, time, math, requests
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

# 阿里云配置（公开版通过环境变量注入，避免硬编码密钥）
API_URL = os.environ.get("ALIYUN_API_URL", "").rstrip("/") + "/chat/completions"
API_KEY = os.environ.get("ALIYUN_API_KEY", "")
MODEL = os.environ.get("GLM_MODEL", "glm-5.2")

def llm(prompt, model=MODEL, max_tokens=4000, temperature=0.1, retries=10):
    for attempt in range(retries):
        try:
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": temperature}
            resp = requests.post(API_URL, json=body,
                headers={"Authorization": "***" + " " + API_KEY}, timeout=(20, 300))
            if resp.status_code == 429 or resp.status_code == 503:
                wait = 10 * (attempt + 1)
                print(f"  [限流{resp.status_code}] wait {wait}s (attempt {attempt+1})", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"].get("content") or ""
            if not content.strip():
                print(f"  [empty] wait {8*(attempt+1)}s (attempt {attempt+1})", flush=True)
                time.sleep(8 * (attempt + 1))
                continue
            return content
        except requests.exceptions.Timeout:
            print(f"  [timeout] wait {8*(attempt+1)}s (attempt {attempt+1})", flush=True)
            time.sleep(8 * (attempt + 1))
        except requests.exceptions.HTTPError as e:
            print(f"  [HTTP {e}] (attempt {attempt+1})", flush=True)
            if attempt == retries - 1:
                raise
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"  [ERR {e}] (attempt {attempt+1})", flush=True)
            if attempt == retries - 1:
                raise
            time.sleep(5 * (attempt + 1))

def extract_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    i, j = text.find("["), text.rfind("]")
    if i >= 0 and j > i and (text.find("{") < 0 or i < text.find("{")):
        text = text[i:j+1]
    else:
        i, j = text.find("{"), text.rfind("}")
        if i >= 0 and j > i:
            text = text[i:j+1]
    text = re.sub(r",\s*([}\]])", r"\1", text)   # 容错：尾随逗号
    text = re.sub(r"//.*?\n", "", text)            # 容错：行注释
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

# ---------- ① 结构提取 ----------
def extract_variant_struct(concept_name, variants):
    slist = []
    for i, v in enumerate(variants):
        slist.append(f"[{i+1}] label={v.get('label','?')} | polarity={v.get('polarity', v.get('type','?'))} | stance={(v.get('stance') or '')[:100]}")
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
    out = llm(prompt, max_tokens=4000)
    try:
        obj = extract_json(out)
        return obj.get("themes", []), obj.get("variants", [])
    except Exception as e:
        print(f"  [提取失败] {e}", flush=True)
        return None, None

# ---------- ② 公理 1 判定 ----------
def axiom1_audit(concept_name, variants):
    slist = []
    for i, v in enumerate(variants):
        slist.append(f"[{i+1}] label={v.get('label','?')} | stance={(v.get('stance') or '')[:100]} | shared_event={(v.get('shared_event') or '')[:60]} | prediction={(v.get('prediction_text') or '')[:60]}")
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
    out = llm(prompt, max_tokens=4000)
    try:
        arr = extract_json(out)
        return arr
    except Exception as e:
        print(f"  [判定失败] {e}", flush=True)
        return None

# ---------- ③ 核验层 ----------
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

# ---------- 判决 ----------
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

def decide_mu(card, mu_star_lo=0.037, mu_star_hi=0.105):
    mu = card["mu"]
    if mu >= mu_star_hi:
        return "互斥超临界", [f"S7(μ): μ={mu:.3f}>={mu_star_hi}"]
    elif mu >= mu_star_lo:
        return "临界", [f"S7(μ): μ={mu:.3f}∈[{mu_star_lo},{mu_star_hi}]"]
    else:
        return "低互斥/有效", [f"S7(μ): μ={mu:.3f}<{mu_star_lo}"]

def reaudit(name, card, mode):
    print(f"\n===== {name}（{mode}，GLM5.2-阿里云）=====", flush=True)
    variants = card.get("variants", [])
    if not variants:
        return None
    themes, structs = extract_variant_struct(name, variants)
    if structs is None or len(structs) != len(variants):
        print(f"  提取数量不匹配，跳过", flush=True)
        return None
    sid_map = {s.get("id", f"v{i+1}"): s for i, s in enumerate(structs)}
    for i, v in enumerate(variants):
        s = sid_map.get(v.get("id", f"v{i+1}"), {})
        v["shared_event"] = s.get("shared_event")
        v["prediction_type"] = s.get("prediction_type")
        v["prediction_text"] = s.get("prediction_text")
        v["is_anchored_v"] = bool(s.get("is_anchored"))
        v["anchor_interface"] = s.get("anchor_interface")
        v["theme"] = s.get("theme")

    audits = axiom1_audit(name, variants)
    if audits is None or len(audits) != len(variants):
        print("  公理 1 判定数量不匹配，跳过", flush=True)
        return None
    aid_map = {a.get("id", f"v{i+1}"): a for i, a in enumerate(audits)}
    n_anchor_law1 = 0
    for i, v in enumerate(variants):
        a = aid_map.get(v.get("id", f"v{i+1}"), {})
        v["axiom1"] = a
        v["is_anchored_law1"] = bool(a.get("is_anchored"))
        if v["is_anchored_law1"]:
            n_anchor_law1 += 1

    av = [v for v in variants if v.get("is_anchored_law1")]
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
    align = round(sum(scores) / len(scores), 3) if scores else None

    thetas = [theta_of(v.get("prediction_type")) for v in variants]
    vec2 = [[polarity_enc(v.get("polarity", "")), event_enc(v.get("prediction_type"))] for v in variants]
    theme_list = [t for t in (themes or [])]
    vec3 = [vec2[i] + [1.0 if (v.get("theme") or "") == tt else 0.0 for tt in theme_list]
            for i, v in enumerate(variants)]
    r, n_theta = kuramoto_r(thetas)
    r2, r3 = rd_of(vec2), rd_of(vec3)
    N = len(variants)
    A_v = n_anchor_law1 / N if N else 0.0

    card2 = dict(card)
    card2["mode"] = mode
    card2["llm"] = "glm-5.2(aliyun)"
    card2["N"] = N
    card2["themes"] = themes
    card2["A_rate_variant_law1"] = round(A_v, 3)
    card2["A_rate_comment"] = card.get("A_rate_comment", card.get("A_rate", 0))
    card2["A_rate"] = round(card.get("A_rate_comment", card.get("A_rate", 0)), 3)
    card2["n_anchor_law1"] = n_anchor_law1
    card2["r_theta"] = round(r, 3)
    card2["r_confidence"] = "高" if n_theta >= 5 else ("中" if n_theta >= 3 else "低")
    card2["r2_axis"] = round(r2, 3)
    card2["r3_axis"] = round(r3, 3)
    card2["delta_r"] = round(r2 - r3, 3)
    card2["n_theta_variants"] = n_theta
    card2["align"] = align
    card2["align_n"] = len(scores)
    card2["verify"] = {"verified": len(results), "results": results}

    if mode == "文献":
        verdict, notes = decide_mu(card2)
        card2["verdict"] = verdict
        card2["verdicts_detail"] = notes
        card2["M"] = card.get("M", 0)
        card2["mu"] = card.get("mu", 0)
    else:
        verdict, notes = decide(card2)
        card2["verdict"] = verdict
        card2["verdicts_detail"] = notes
        if align is not None and card2["A_rate"] < 0.25 and r >= 0.6 and align < 0.5:
            card2["verdict"] = "无锚假收敛"
            card2["verdicts_detail"].append(f"S9: 假收敛转正(r={r:.2f} ∧ align={align:.2f})")
    print(f"  N={N} A_rate(第一律)={A_v:.3f} 评论级={card2['A_rate']:.3f} r={r:.3f}[{card2['r_confidence']}] Δr={card2['delta_r']:+.3f} align={align} (n={len(scores)})", flush=True)
    print(f"  → 判决: {card2['verdict']}", flush=True)
    return card2

def main():
    out = json.load(open(os.path.join(BASE, "mutex_audit_v6_glm52_partial.json"), encoding="utf-8"))
    print(f"断点续跑：已有 {len(out)} 个概念（SiliconFlow 完成）", flush=True)
    # 语料模式（跳过已完成的）
    v52 = json.load(open(os.path.join(BASE, "mutex_audit_v5_2.json"), encoding="utf-8"))
    for name, card in v52.items():
        if not card or name in out:
            continue
        r = reaudit(name, card, "语料")
        if r:
            out[name] = r
            with open(os.path.join(BASE, "mutex_audit_v6_glm52.json"), "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
    # 文献模式
    th = json.load(open(os.path.join(BASE, "theories_audit_v2.json"), encoding="utf-8"))
    for name, card in th.items():
        if not card:
            continue
        key = "文献_" + name
        if key in out:
            continue
        r = reaudit(name, card, "文献")
        if r:
            out[key] = r
            with open(os.path.join(BASE, "mutex_audit_v6_glm52.json"), "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(BASE, "mutex_audit_v6_glm52.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n已存 mutex_audit_v6_glm52.json（{len(out)} 个概念）", flush=True)

    # 对照 v5.6
    print("\n===== 消融对照：deepseek(v5.6) vs GLM5.2(v6) =====", flush=True)
    v56 = json.load(open(os.path.join(BASE, "mutex_audit_v5_6_law1.json"), encoding="utf-8"))
    stable = 0
    total = 0
    for name, c in out.items():
        if "verdict" not in c:
            continue
        total += 1
        old = v56.get(name, {})
        old_v = old.get("verdict", "?")
        new_v = c.get("verdict", "?")
        same = (old_v == new_v)
        if same:
            stable += 1
        print(f"  {name}: v5.6[{old_v}] → v6[{new_v}] {'✓' if same else '✗ 变化'}", flush=True)
    print(f"\n判决稳定性: {stable}/{total} ({stable/total:.1%})", flush=True)

if __name__ == "__main__":
    main()
