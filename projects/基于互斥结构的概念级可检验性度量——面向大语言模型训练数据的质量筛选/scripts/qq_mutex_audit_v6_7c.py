# -*- coding: utf-8 -*-
"""v6.7c：decide_lit A 取值最终修正——评论级>0 优先，否则变体级
伪史论（A_c=0.045）→ 悬空；幸存者（A_c=0 → A_v=1.0）→ 有效
"""
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

MU_LO, MU_HI, P_STAR = 0.037, 0.105, 0.25

def decide_lit(card):
    mu = card.get("mu", 0)
    A_c = card.get("A_rate_comment")
    A_v = card.get("A_rate_variant_law1", card.get("A_rate_variant", 0))
    A = A_c if (A_c is not None and A_c > 0) else (A_v or 0)
    if mu >= MU_HI:
        return "互斥超临界", f"μ={mu:.3f}>={MU_HI}"
    elif mu >= MU_LO:
        return "临界", f"μ={mu:.3f}∈[{MU_LO},{MU_HI})"
    else:
        if A >= P_STAR:
            return "低互斥/有效", f"μ={mu:.3f}<{MU_LO} ∧ A={A:.3f}>={P_STAR}"
        else:
            return "无锚（悬空）", f"μ={mu:.3f}<{MU_LO} ∧ A={A:.3f}<{P_STAR} → 低互斥+低锚定=悬空"

def main():
    out_path = os.path.join(BASE, "mutex_audit_v6_glm52.json")
    v56_path = os.path.join(BASE, "mutex_audit_v5_6_law1_fixed.json")
    out = json.load(open(out_path, encoding="utf-8"))
    v56 = json.load(open(v56_path, encoding="utf-8"))

    for store, tag in [(out, "GLM"), (v56, "DS")]:
        for k in list(store.keys()):
            c = store[k]
            if not c or "verdict" not in c:
                continue
            is_lit = k.startswith("文献_") or c.get("mode") == "文献" or k == "西方伪史论(文献枚举)"
            if is_lit:
                v, note = decide_lit(c)
                c["verdict"] = v
                c["verdicts_detail"] = [f"S7(μ+A 组合): {note}"]
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(v56, open(v56_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("===== 最终消融对照（v6.7c）：deepseek vs GLM5.2 =====", flush=True)
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
