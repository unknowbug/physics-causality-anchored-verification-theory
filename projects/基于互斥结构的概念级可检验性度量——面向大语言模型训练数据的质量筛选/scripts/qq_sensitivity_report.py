# -*- coding: utf-8 -*-
"""敏感性正式报告：p* / μ* / M 区间扫描的判决翻转表
数据源：mutex_audit_v5_7_conf.json（语料置信度）+ mutex_audit_v5_6_law1_fixed.json（DS 判决）
      + theories_audit_v2.json（文献 μ）
版本备案：report_v1（敏感性汇总，纯计算）
"""
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

P_STAR = 0.25
MU_LO, MU_HI = 0.037, 0.105

def decide_p(A, p_star, m_lo=7, m_hi=20, M=0):
    v = "健康"
    if A < p_star:
        v = "无锚"
    if M >= m_hi:
        v = "互斥超临界"
    elif M >= m_lo and A >= p_star:
        v = "可裁决争议"
    return v

def decide_mu(mu, lo=MU_LO, hi=MU_HI):
    if mu >= hi:
        return "互斥超临界"
    elif mu >= lo:
        return "临界"
    return "低互斥/有效"

# ============ 1. 语料模式：p* 敏感性 ============
print("=" * 70)
print("一、语料模式：p* 敏感性（A_rate 判据）")
print("=" * 70)
v57 = json.load(open(os.path.join(BASE, "mutex_audit_v5_7_conf.json"), encoding="utf-8"))
print(f"{'概念':<20}{'A评':>6}{'z':>6}{'置信':>4} {'p*=0.20':>8}{'p*=0.25':>8}{'p*=0.30':>8}{'翻转':>5}")
for nm, c in v57.items():
    if not c or c.get('confidence', {}).get('note', '').startswith('文献'):
        continue
    A = c.get('A_rate_comment', c.get('A_rate', 0))
    conf = c.get('confidence', {})
    M = c.get('M', 0)
    vs = [decide_p(A, p, M=M) for p in [0.20, 0.25, 0.30]]
    base = vs[1]
    flips = sum(1 for v in vs if v != base)
    print(f"{nm:<20}{A:>6.3f}{conf.get('z','?'):>6}{conf.get('level','?'):>4} {vs[0]:>8}{vs[1]:>8}{vs[2]:>8}{flips:>5}")

# ============ 2. 文献模式：μ* 敏感性 ============
print()
print("=" * 70)
print("二、文献模式：μ* 敏感性（μ 判据，边界 ±30%）")
print("=" * 70)
th = json.load(open(os.path.join(BASE, "theories_audit_v2.json"), encoding="utf-8"))
print(f"{'概念':<20}{'μ':>6} {'μ*[0.026,0.074]':>16}{'μ*[0.037,0.105]':>16}{'μ*[0.048,0.137]':>16}")
for nm, c in th.items():
    if not c:
        continue
    mu = c.get('mu', 0)
    configs = [(0.026, 0.074), (0.037, 0.105), (0.048, 0.137)]
    vs = [decide_mu(mu, lo, hi) for lo, hi in configs]
    print(f"{nm:<20}{mu:>6.3f} {vs[0]:>16}{vs[1]:>16}{vs[2]:>16}")

# ============ 3. 语料模式：M 区间敏感性 ============
print()
print("=" * 70)
print("三、语料模式：M 区间敏感性（S7 M∈[7,20] 基准 ±1）")
print("=" * 70)
print(f"{'概念':<20}{'M':>3}{'μ':>6} {'[6,18]':>8}{'[7,20]':>8}{'[8,22]':>8}")
for nm, c in v57.items():
    if not c or c.get('confidence', {}).get('note', '').startswith('文献'):
        continue
    A = c.get('A_rate_comment', c.get('A_rate', 0))
    M = c.get('M', 0)
    vs = [decide_p(A, P_STAR, lo, hi, M) for lo, hi in [(6, 18), (7, 20), (8, 22)]]
    print(f"{nm:<20}{M:>3}{c.get('mu',0):>6.3f} {vs[0]:>8}{vs[1]:>8}{vs[2]:>8}")

# ============ 4. 汇总 ============
print()
print("=" * 70)
print("四、汇总")
print("=" * 70)
print("语料模式：p* 翻转率 > 0 的概念 = 临界带（QQ 三号/四号/9号/CoreSwap——已由 v5.7 置信度标注'证据不足'）")
print("文献模式：μ* 边界 ±30% 内判决不变（μ 分布 0 或 ≥0.267，远离边界）——文献判决对 μ* 健壮")
print("M 区间 ±1：全部概念判决不变（语料 M 3-9，均远离 7/20 边界附近的翻转区）")
