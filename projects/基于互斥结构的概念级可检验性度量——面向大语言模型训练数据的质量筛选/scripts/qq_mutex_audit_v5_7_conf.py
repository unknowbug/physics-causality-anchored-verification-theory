# -*- coding: utf-8 -*-
"""v5.7：判决函数加显式置信度（问题 1 实现）
方案（指挥官 2026-08-12）：二态判决 + 显式置信度，不做三态
- 置信度 = A_rate 的统计分辨力：SE = sqrt(A(1-A)/N)，z = |A - p*| / SE
- 样本量 N = 变体覆盖评论数（保守，不用全量评论）
- 置信等级：z>=2 高 / 1<=z<2 中 / z<1 低（证据不足）
- 判决保持二态（无锚/达标），置信度低标注"证据不足"
- 敏感性分析改为置信度分布报告
版本备案：v5.7（判决函数升级，无 LLM，纯本地计算）
"""
import json, io, sys, math, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

P_STAR = 0.25

def confidence_of(A, N):
    """二项标准误 + z 值 + 置信等级"""
    if N <= 0 or A <= 0 or A >= 1:
        # 极端比例用 Wilson 下限保守估计
        se = math.sqrt(max(A * (1 - A), 1e-6) / max(N, 1))
    else:
        se = math.sqrt(A * (1 - A) / N)
    z = abs(A - P_STAR) / se if se > 0 else 99.0
    if z >= 2.0:
        level = "高"
    elif z >= 1.0:
        level = "中"
    else:
        level = "低"
    insufficient = z < 1.0
    return {"A_rate": round(A, 4), "N": N, "SE": round(se, 4), "z": round(z, 3),
            "level": level, "insufficient": insufficient,
            "note": "证据不足（|A-p*|<1SE），需更多样本" if insufficient else ""}

def main():
    src = json.load(open(os.path.join(BASE, 'mutex_audit_v5_6_law1.json'), encoding='utf-8'))
    out = {}
    print(f"{'概念':<26}{'A评':>7}{'N':>6}{'SE':>7}{'z':>6}{'置信':>4}  {'判决':<8} 标注")
    for name, c in src.items():
        if not c:
            continue
        # 文献模式无评论级 A_rate（无评论数据），置信度不适用
        if name.startswith("文献_") or c.get("mode") == "文献枚举":
            c["confidence"] = {"note": "文献模式无评论级样本，置信度不适用（判决用 μ 判据）"}
            out[name] = c
            print(f"{name:<26}  (文献模式，置信度不适用，判决用 μ)")
            continue
        # 样本量 = 变体覆盖评论数（保守聚合）
        N = 0
        for v in c.get("variants", []):
            N += int(v.get("comments", 0) or 0)
        if N == 0:
            N = int(c.get("comments", 400) or 400)
        A = c.get("A_rate_comment", c.get("A_rate", 0))
        conf = confidence_of(A, N)
        c["confidence"] = conf
        c["verdicts_detail"] = c.get("verdicts_detail", []) + (
            [f"置信度: {conf['level']}(z={conf['z']}, SE={conf['SE']})" +
             (f"——{conf['note']}" if conf['insufficient'] else "")]
        )
        out[name] = c
        mark = "⚠️证据不足" if conf["insufficient"] else ("✓" if conf["level"] == "高" else "~中")
        print(f"{name:<26}{A:>7.3f}{N:>6}{conf['SE']:>7.3f}{conf['z']:>6.2f}{conf['level']:>4}  "
              f"{c['verdict']:<8} {mark}")

    with open(os.path.join(BASE, 'mutex_audit_v5_7_conf.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n已存 mutex_audit_v5_7_conf.json（判决卡+置信度字段，未覆盖旧文件）", flush=True)

    # 敏感性分析改为置信度分布
    print("\n===== 临界带概念的置信度判定（替代硬切）=====")
    for name, c in out.items():
        if not c:
            continue
        conf = c.get("confidence", {})
        if conf.get("insufficient"):
            print(f"  {name}: A_rate={conf['A_rate']:.3f} z={conf['z']:.2f} → 证据不足，"
                  f"判决[{c['verdict']}]保留但标注低置信")

if __name__ == "__main__":
    main()
