# -*- coding: utf-8 -*-
"""互斥审查器 v5.2：外部核验层（align 计算）
对 v5.1 判决卡中 is_anchored_v=True 的变体执行外部核验：
1. LLM 核验：检验接口真实存在性 + 事件客观结果 + 置信度
2. align（S9 方向判据）= 预测方向与事实结果一致的比例（确定性计算）
3. 判决更新：A_rate<p* 且 r≥0.6 且 align<0.5 → 无锚假收敛（S9 转正）
标注：LLM 核验为预审，关键概念需人工/检索抽查复核（伪史论将单独核对）
版本备案：v5.2（新增核验 prompt，独立脚本）
"""
import json, os, sys, re, time, math, requests

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

def llm(prompt, model="deepseek-chat", max_tokens=2000, temperature=0.1, retries=3):
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
2. factual_outcome: 该事件当前已知的客观结果（依据公开事实、学界共识、公开数据）——"发生"（预测方向成立）/ "不发生"（不成立）/ "未知"（无公认结果或不可判定）。注意：只依据客观已有结果，不推测。
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
    """一致性评分：一致=1, 不一致=0, 条件/未知=中性(不计入)"""
    if outcome in ("发生", "不发生"):
        if prediction_type == "发生":
            return 1.0 if outcome == "发生" else 0.0
        if prediction_type == "不发生":
            return 1.0 if outcome == "不发生" else 0.0
    return None

def update_card(name, card):
    print(f"\n===== {name} 外部核验 =====", flush=True)
    av = [v for v in card.get("variants", []) if v.get("is_anchored_v")]
    if not av:
        card["verify"] = {"verified": 0, "note": "无 A 锚变体可核验"}
        return card
    results = []
    scores = []
    for v in av:
        r = verify_variant(name, v)
        if r is None:
            v["verify"] = {"error": True}
            results.append({"variant": v.get("id"), "error": True})
            continue
        v["verify"] = r
        results.append({"variant": v.get("id"), **r})
        sc = align_score(v.get("prediction_type"), r.get("factual_outcome"))
        if sc is not None:
            scores.append(sc)
        print(f"  {v.get('id')} [{v.get('label','')}] 接口存在={r.get('interface_exists')} "
              f"事实结果={r.get('factual_outcome')} 置信={r.get('confidence')} "
              f"预测={v.get('prediction_type')} → align={sc}", flush=True)
    align = sum(scores) / len(scores) if scores else None
    card["align"] = round(align, 3) if align is not None else None
    card["align_n"] = len(scores)
    card["verify"] = {"verified": len(results), "results": results,
                      "note": "LLM 预审，关键概念需人工抽查复核"}

    # 判决更新：S9 假收敛转正
    A = card["A_rate"]
    r_theta = card.get("r_theta", 0)
    if align is not None:
        if A < 0.25 and r_theta >= 0.6 and align < 0.5:
            card["verdict"] = "无锚假收敛"
            card["verdicts_detail"].append(f"S9: 假收敛转正(r={r_theta:.2f}高 ∧ align={align:.2f}低)")
        else:
            card["verdicts_detail"].append(f"S9: align={align:.2f}({'真收敛方向' if align >= 0.5 else '低'})")
    print(f"  → align={align} (n={len(scores)}) | 判决: {card['verdict']}", flush=True)
    return card

def main():
    src = json.load(open(os.path.join(BASE, "mutex_audit_v5_1.json"), encoding="utf-8"))
    for name, card in src.items():
        if card:
            update_card(name, card)
    with open(os.path.join(BASE, "mutex_audit_v5_2.json"), "w", encoding="utf-8") as f:
        json.dump(src, f, ensure_ascii=False, indent=2)
    print("\n已存 mutex_audit_v5_2.json", flush=True)
    print("\n===== v5.2 判决汇总 =====", flush=True)
    for name, c in src.items():
        if c is None:
            continue
        print(f"{name}: align={c.get('align')} (n={c.get('align_n',0)}) A_rate={c['A_rate']:.3f} "
              f"r={c['r_theta']:.3f} → {c['verdict']}", flush=True)

if __name__ == "__main__":
    main()
