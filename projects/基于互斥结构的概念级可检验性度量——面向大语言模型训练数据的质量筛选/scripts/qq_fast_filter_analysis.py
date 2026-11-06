# -*- coding: utf-8 -*-
"""快速严格过滤器：规则特征 vs LLM 锚定判定（2000 条）对齐分析
目标：找到"跑得快且严格"的特征组合（宁可误杀，不漏放）
金标准：qq_anchored_judged.json 的 has_anchor（LLM 判定，2000 条）
产出：单特征区分度 + 组合打分器精确率/召回率/F1
版本备案：v1.0（分析脚本，无 LLM，纯本地计算）
"""
import json, io, sys, re, math, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

data = json.load(open(os.path.join(BASE, 'qq_anchored_judged.json'), encoding='utf-8'))
rows = []
for g, items in data.items():
    for it in items:
        rows.append({"group": g, "msg": it.get("message", ""), "anchor": bool(it.get("has_anchor"))})
print(f"总条数: {len(rows)} | 有锚: {sum(1 for r in rows if r['anchor'])} "
      f"({sum(1 for r in rows if r['anchor'])/len(rows):.3f})")

# ---------- 规则特征定义 ----------
def feats(msg):
    m = msg or ""
    f = {}
    # 正向（可检验性信号）
    f["数字"] = bool(re.search(r'\d', m))
    f["量化单位"] = bool(re.search(r'\d+\s*(万|亿|元|块|年|月|日|次|倍|%|％|个|条|人|张|台|款|亿|万亿)', m))
    f["条件句"] = bool(re.search(r'如果|若|除非|只有.{0,6}才|只要|一旦', m))
    f["因果词"] = bool(re.search(r'因为|所以|导致|由于|造成|意味着', m))
    f["引证"] = bool(re.search(r'说|称|报道|数据显示|研究表明|研究表明|统计|调查显示|报道称', m))
    f["具体时间"] = bool(re.search(r'\d{4}年|\d+月\d+日|去年|今年|上个月|上周|昨天|前天', m))
    # 负向（病态信号）
    f["绝对化"] = bool(re.search(r'永远|必然|一定|绝对|根本|完全|一切|所有|任何|从来|彻底|毫无', m))
    f["情绪词"] = bool(re.search(r'垃圾|傻|废物|恶心|笑死|服了|离谱|脑残|煞笔|沙雕|吐了|绝了|逆天', m))
    f["反问感叹"] = bool(re.search(r'[？！]{2,}|[?]{2,}|[!]{2,}|呢[？?]|吗[？?]', m))
    f["身份标签"] = bool(re.search(r'觉醒|粉红|美分|公知|1450|殖人|恨国|走狗|汉奸|卖国|小粉红|润人', m))
    f["长度过短"] = len(m) < 8
    f["长度过长"] = len(m) > 200
    return f

# ---------- 单特征区分度 ----------
print("\n===== 单特征 vs has_anchor =====")
N = len(rows)
n_anchor = sum(1 for r in rows if r['anchor'])
feat_stats = {}
for r in rows:
    fs = feats(r['msg'])
    for k, v in fs.items():
        if k not in feat_stats:
            feat_stats[k] = {"hit": 0, "hit_anchor": 0, "miss": 0, "miss_anchor": 0}
        if v:
            feat_stats[k]["hit"] += 1
            if r['anchor']:
                feat_stats[k]["hit_anchor"] += 1
        else:
            feat_stats[k]["miss"] += 1
            if r['anchor']:
                feat_stats[k]["miss_anchor"] += 1

base_rate = n_anchor / N
print(f"基线有锚率: {base_rate:.3f}")
print(f"{'特征':<10}{'命中':>6}{'命中率':>8}{'命中时有锚':>10}{'未命中时有锚':>10}{'区分度':>8}  方向")
results = []
for k, s in feat_stats.items():
    hit_rate = s['hit'] / s['hit'] if s['hit'] else 0
    hit_anchor = s['hit_anchor'] / s['hit'] if s['hit'] else base_rate
    miss_anchor = s['miss_anchor'] / s['miss'] if s['miss'] else base_rate
    lift = hit_anchor - miss_anchor
    direction = "正向" if lift > 0 else "负向"
    results.append((k, s['hit'], hit_anchor, miss_anchor, lift, direction))
    print(f"{k:<10}{s['hit']:>6}{hit_rate:>8.3f}{hit_anchor:>10.3f}{miss_anchor:>10.3f}{lift:>+8.3f}  {direction}")

# ---------- 组合打分器 ----------
print("\n===== 组合打分器（正特征+1，负特征-1）=====")
POS = ["数字", "量化单位", "条件句", "因果词", "引证", "具体时间"]
NEG = ["绝对化", "情绪词", "反问感叹", "身份标签", "长度过短", "长度过长"]
scored = []
for r in rows:
    fs = feats(r['msg'])
    score = sum(1 for k in POS if fs.get(k)) - sum(1 for k in NEG if fs.get(k))
    scored.append((score, r['anchor']))

# 扫描阈值（严格侧：高分才放行）
print(f"{'阈值≥':>6}{'放行':>6}{'放行中有锚':>10}{'召回':>8}{'精确率':>8}{'F1':>8}  含义")
best = None
for thr in range(-2, 5):
    passed = [(s, a) for s, a in scored if s >= thr]
    if not passed:
        continue
    n_p = len(passed)
    n_pa = sum(1 for _, a in passed if a)
    recall = n_pa / n_anchor
    prec = n_pa / n_p if n_p else 0
    f1 = 2 * prec * recall / (prec + recall) if (prec + recall) else 0
    print(f"{thr:>6}{n_p:>6}{n_pa/n_p:>10.3f}{recall:>8.3f}{prec:>8.3f}{f1:>8.3f}  "
          f"{'严格' if thr >= 2 else ('平衡' if thr == 1 else '宽松')}")
    if best is None or f1 > best[1]:
        best = (thr, f1, prec, recall, n_pa, n_p)
print(f"\n最佳阈值: ≥{best[0]}  F1={best[1]:.3f} 精确率={best[2]:.3f} 召回={best[3]:.3f} "
      f"(放行 {best[4]}/{best[5]} 条)")

# 严格侧重点：高精确率（宁可误杀）
print("\n===== 严格档位（高精确率优先）=====")
for thr in range(2, 6):
    passed = [(s, a) for s, a in scored if s >= thr]
    if not passed:
        continue
    n_pa = sum(1 for _, a in passed if a)
    print(f"阈值≥{thr}: 放行 {len(passed)} 条, 其中锚定 {n_pa} 条, 锚定比例={n_pa/len(passed):.3f} "
          f"(基线 {base_rate:.3f})")
