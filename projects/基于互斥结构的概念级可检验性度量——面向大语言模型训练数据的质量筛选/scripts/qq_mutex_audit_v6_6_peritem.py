# -*- coding: utf-8 -*-
"""互斥审查器 v6.6：伪史论 GLM5.2 补跑——逐变体单对象 + 并发
版本备案：v6.6（数组输出崩 → 逐变体单对象 JSON，GLM-5.2 单对象稳定）
提取/判定/核验全部逐变体（单对象 JSON），ThreadPool 并发 3
"""
import json, os, sys, re, time, math, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

API_URL = os.environ.get("ALIYUN_API_URL", "").rstrip("/") + "/chat/completions"
API_KEY = os.environ.get("ALIYUN_API_KEY", "")
MODEL = os.environ.get("GLM_MODEL", "glm-5.2")
MAX_WORKERS = 3
_lock = threading.Lock()

def llm(prompt, model=MODEL, max_tokens=2000, temperature=0.1, retries=12):
    for attempt in range(retries):
        try:
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens, "temperature": temperature}
            resp = requests.post(API_URL, json=body,
                headers={"Authorization": "***" + " " + API_KEY}, timeout=(20, 240))
            if resp.status_code in (429, 503):
                wait = 8 * (attempt + 1)
                print(f"  [限流{resp.status_code}] wait {wait}s", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"].get("content") or ""
            if not content.strip():
                print(f"  [empty] wait {6*(attempt+1)}s", flush=True)
                time.sleep(6 * (attempt + 1))
                continue
            return content
        except requests.exceptions.Timeout:
            print(f"  [timeout] wait {6*(attempt+1)}s", flush=True)
            time.sleep(6 * (attempt + 1))
        except Exception as e:
            print(f"  [ERR {e}] (attempt {attempt+1})", flush=True)
            if attempt == retries - 1:
                raise
            time.sleep(4 * (attempt + 1))

def extract_json(text):
    """raw_decode：解析第一个完整 JSON 值（单对象最稳）"""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    dec = json.JSONDecoder()
    for ch in "[{":
        i = text.find(ch)
        if i >= 0:
            try:
                obj, _ = dec.raw_decode(text[i:])
                return obj
            except Exception:
                continue
    # 兜底：尾随逗号 + 中文引号
    t2 = re.sub(r",\s*([}\]])", r"\1", text)
    t2 = t2.replace("“", '"').replace("”", '"')
    return json.loads(t2)

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

# ---------- 逐变体提取 ----------
def extract_one(concept_name, v, idx):
    prompt = f"""你是变体结构分析器。概念「{concept_name}」的第 {idx} 个变体：
label={v.get('label','?')} | polarity={v.get('polarity', v.get('type','?'))} | stance={(v.get('stance') or '')[:120]}

输出该变体的结构化字段：
- shared_event: 该变体预测针对的可公共观测事件。若不针对任何可观测事件，输出 null。
- prediction_type: "发生"/"不发生"/"条件"/"无预测"。
- prediction_text: 预测内容简述（无预测则 null）。
- is_anchored: 是否携带至少一个可被独立观测者确认或否定的预测（true/false）。
- anchor_interface: 检验接口描述。无则 null。
- theme: 主题标签（3-6 字）。

只输出单个 JSON 对象（不要任何解释、不要代码块标记）：
{{"id": "v{idx}", "shared_event": ..., "prediction_type": ..., "prediction_text": ..., "is_anchored": ..., "anchor_interface": ..., "theme": ...}}"""
    for attempt in range(4):
        out = llm(prompt, max_tokens=1500)
        try:
            return extract_json(out)
        except Exception as e:
            print(f"  [提取失败 v{idx} attempt {attempt+1}/4: {e}]", flush=True)
            time.sleep(2)
    return None

# ---------- 逐变体公理 1 判定 ----------
def axiom_one(concept_name, v, idx):
    prompt = f"""你是第一律检验方案审查员。概念「{concept_name}」的第 {idx} 个变体：
label={v.get('label','?')} | stance={(v.get('stance') or '')[:120]} | shared_event={(v.get('shared_event') or '')[:60]}

按第一律（公理 1：声称 C 有效 ⇒ ∃检验方案 T(C)：T 在有限步骤内完成 ∧ T 结果可公共观测，锚定 A1 管辖的物理结果）判定其是否锚定：
- has_check_plan: 是否存在**具体可执行的检验方案**（明确操作流程——不是"理论上可验证"）
- plan: 检验方案描述（30-60 字；无则 null）
- terminus: 论证链终点——"物理结果"/"概念"/"无方案"
- finite_steps: 方案是否有限步骤可执行（true/false；无方案则 false）
- public_observable: 结果是否可公共观测（true/false；无方案则 false）
- self_contained: 是否自足定义/自我闭合（true/false）
- is_anchored: 三要件全满足且非自足定义才为 true
- reason: 判定依据（30 字内）

只输出单个 JSON 对象（不要任何解释、不要代码块标记）：
{{"id": "v{idx}", "has_check_plan": true, "plan": "...", "terminus": "物理结果", "finite_steps": true, "public_observable": true, "self_contained": false, "is_anchored": true, "reason": "..."}}"""
    for attempt in range(4):
        out = llm(prompt, max_tokens=1500)
        try:
            return extract_json(out)
        except Exception as e:
            print(f"  [判定失败 v{idx} attempt {attempt+1}/4: {e}]", flush=True)
            time.sleep(2)
    return None

# ---------- 核验（逐变体，单对象） ----------
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
2. factual_outcome: 该事件当前已知的客观结果——"发生"/"不发生"/"未知"。
3. confidence: 高/中/低
4. basis: 依据简述（30 字内）

只输出单个 JSON 对象：
{{"interface_exists": true, "factual_outcome": "不发生", "confidence": "高", "basis": "依据"}}"""
    for attempt in range(3):
        out = llm(prompt, max_tokens=1000)
        try:
            return extract_json(out)
        except Exception as e:
            print(f"  [核验失败 {label} attempt {attempt+1}/3] 重试", flush=True)
            time.sleep(2)
    return None

def align_score(prediction_type, outcome):
    if outcome in ("发生", "不发生"):
        if prediction_type == "发生":
            return 1.0 if outcome == "发生" else 0.0
        if prediction_type == "不发生":
            return 1.0 if outcome == "不发生" else 0.0
    return None

def decide_mu(card, mu_star_lo=0.037, mu_star_hi=0.105):
    mu = card["mu"]
    if mu >= mu_star_hi:
        return "互斥超临界", [f"S7(μ): μ={mu:.3f}>={mu_star_hi}"]
    elif mu >= mu_star_lo:
        return "临界", [f"S7(μ): μ={mu:.3f}∈[{mu_star_lo},{mu_star_hi}]"]
    else:
        return "低互斥/有效", [f"S7(μ): μ={mu:.3f}<{mu_star_lo}"]

def pmap(items, fn, label):
    """并发 map：items = [(key, *args)]，返回 {key: result}"""
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {}
        for key, *args in items:
            futs[ex.submit(fn, *args)] = key
        for f in as_completed(futs):
            key = futs[f]
            try:
                results[key] = f.result()
            except Exception as e:
                print(f"  [{label} {key} 异常 {e}]", flush=True)
                results[key] = None
    return results

def main():
    name = "西方伪史论(文献枚举)"
    v52 = json.load(open(os.path.join(BASE, "mutex_audit_v5_2.json"), encoding="utf-8"))
    card = v52.get(name)
    variants = card.get("variants", [])
    N = len(variants)
    print(f"===== {name}（{N} 变体，GLM5.2 逐变体并发 {MAX_WORKERS}）=====", flush=True)

    # ① 逐变体提取（并发）
    print("① 提取（并发）...", flush=True)
    structs = pmap([(i + 1, name, v, i + 1) for i, v in enumerate(variants)], extract_one, "提取")
    if any(structs.get(i + 1) is None for i in range(N)):
        print("提取有失败，退出", flush=True)
        return
    for i, v in enumerate(variants):
        s = structs[i + 1]
        v["shared_event"] = s.get("shared_event")
        v["prediction_type"] = s.get("prediction_type")
        v["prediction_text"] = s.get("prediction_text")
        v["is_anchored_v"] = bool(s.get("is_anchored"))
        v["anchor_interface"] = s.get("anchor_interface")
        v["theme"] = s.get("theme")
    themes = sorted(set(v.get("theme") for v in variants if v.get("theme")))
    print(f"  提取完成 {N} 变体, {len(themes)} 主题", flush=True)

    # ② 逐变体公理 1 判定（并发）
    print("② 公理 1 判定（并发）...", flush=True)
    audits = pmap([(i + 1, name, v, i + 1) for i, v in enumerate(variants)], axiom_one, "判定")
    if any(audits.get(i + 1) is None for i in range(N)):
        print("判定有失败，退出", flush=True)
        return
    n_anchor_law1 = 0
    for i, v in enumerate(variants):
        a = audits[i + 1]
        v["axiom1"] = a
        v["is_anchored_law1"] = bool(a.get("is_anchored"))
        if v["is_anchored_law1"]:
            n_anchor_law1 += 1
    print(f"  判定完成: {n_anchor_law1}/{N} 锚定", flush=True)

    # ③ 核验（并发）
    print("③ 核验（并发）...", flush=True)
    av = [v for v in variants if v.get("is_anchored_law1")]
    scores, results = [], []
    if av:
        vrs = pmap([(v.get("id"), name, v) for v in av], lambda nm, vv: (vv.get("id"), verify_variant(nm, vv)), "核验")
        for vid, (_, rv) in sorted(vrs.items()):
            vv = next(v for v in av if v.get("id") == vid)
            if rv is None:
                results.append({"variant": vid, "error": True})
                continue
            vv["verify"] = rv
            results.append({"variant": vid, **rv})
            sc = align_score(vv.get("prediction_type"), rv.get("factual_outcome"))
            if sc is not None:
                scores.append(sc)
    align = round(sum(scores) / len(scores), 3) if scores else None
    print(f"  核验完成: align={align} (n={len(scores)})", flush=True)

    # ④ 结构量 + 判决
    thetas = [theta_of(v.get("prediction_type")) for v in variants]
    vec2 = [[polarity_enc(v.get("polarity", "")), event_enc(v.get("prediction_type"))] for v in variants]
    theme_list = [t for t in themes]
    vec3 = [vec2[i] + [1.0 if (v.get("theme") or "") == tt else 0.0 for tt in theme_list]
            for i, v in enumerate(variants)]
    r, n_theta = kuramoto_r(thetas)
    r2, r3 = rd_of(vec2), rd_of(vec3)
    A_v = n_anchor_law1 / N

    card2 = dict(card)
    card2["mode"] = "文献"
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
    verdict, notes = decide_mu(card2)
    card2["verdict"] = verdict
    card2["verdicts_detail"] = notes
    card2["M"] = card.get("M", 0)
    card2["mu"] = card.get("mu", 0)
    print(f"  N={N} A_rate(第一律)={A_v:.3f} r={r:.3f} Δr={card2['delta_r']:+.3f} align={align} → 判决: {verdict}", flush=True)

    # 合并 + 最终对照
    out_path = os.path.join(BASE, "mutex_audit_v6_glm52.json")
    out = json.load(open(out_path, encoding="utf-8"))
    out[name] = card2
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n已合并 {name} → {len(out)} 个概念", flush=True)

    v56 = json.load(open(os.path.join(BASE, "mutex_audit_v5_6_law1_fixed.json"), encoding="utf-8"))
    print("\n===== 最终消融对照（修正基准，15 概念）：deepseek vs GLM5.2 =====", flush=True)
    stable = total = 0
    for nm, c in out.items():
        if "verdict" not in c:
            continue
        total += 1
        old_v = v56.get(nm, {}).get("verdict", "?")
        new_v = c.get("verdict", "?")
        same = (old_v == new_v)
        if same:
            stable += 1
        print(f"  {nm}: deepseek[{old_v}] → GLM5.2[{new_v}] {'✓' if same else '✗'}", flush=True)
    print(f"\n判决稳定性: {stable}/{total} ({stable/total:.1%})", flush=True)

if __name__ == "__main__":
    main()
