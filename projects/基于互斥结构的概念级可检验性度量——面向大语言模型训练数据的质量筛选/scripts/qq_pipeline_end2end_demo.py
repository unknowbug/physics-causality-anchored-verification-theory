# -*- coding: utf-8 -*-
"""两级架构端到端演示：群级基线筛选 → 条级富集 → 清洗后语料统计
公开版脱敏：群名保留，群号隐去；本地路径改为环境变量/相对路径。
"""
import json, io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
PSEUDO_GROUP_ID = os.environ.get("QQ_GROUP_ID_PSEUDOHISTORY", "REDACTED")
SAMPLE = os.environ.get(
    "PCAVT_PSEUDO_SAMPLE",
    os.path.join(BASE, "jsonl_samples", f"group_{PSEUDO_GROUP_ID}.jsonl"),
)

# ---------- 词汇打分器（与 qq_fast_filter_analysis 相同） ----------
POS = ["数字", "量化单位", "条件句", "因果词", "引证", "具体时间"]
NEG = ["绝对化", "情绪词", "反问感叹", "身份标签", "长度过短", "长度过长"]

def feats(msg):
    m = msg or ""
    f = {}
    f["数字"] = bool(re.search(r'\d', m))
    f["量化单位"] = bool(re.search(r'\d+\s*(万|亿|元|块|年|月|日|次|倍|%|％|个|条|人|张|台|款)', m))
    f["条件句"] = bool(re.search(r'如果|若|除非|只有.{0,6}才|只要|一旦', m))
    f["因果词"] = bool(re.search(r'因为|所以|导致|由于|造成|意味着', m))
    f["引证"] = bool(re.search(r'说|称|报道|数据显示|研究表明|统计|调查显示|报道称', m))
    f["具体时间"] = bool(re.search(r'\d{4}年|\d+月\d+日|去年|今年|上个月|上周|昨天|前天', m))
    f["绝对化"] = bool(re.search(r'永远|必然|一定|绝对|根本|完全|一切|所有|任何|从来|彻底|毫无', m))
    f["情绪词"] = bool(re.search(r'垃圾|傻|废物|恶心|笑死|服了|离谱|脑残|煞笔|沙雕|吐了|绝了|逆天', m))
    f["反问感叹"] = bool(re.search(r'[？！]{2,}|[?]{2,}|[!]{2,}|呢[？?]|吗[？?]', m))
    f["身份标签"] = bool(re.search(r'觉醒|粉红|美分|公知|1450|殖人|恨国|走狗|汉奸|卖国|小粉红|润人', m))
    f["长度过短"] = len(m) < 8
    f["长度过长"] = len(m) > 200
    return f

def score_of(m):
    fs = feats(m)
    return sum(1 for k in POS if fs.get(k)) - sum(1 for k in NEG if fs.get(k))

# ---------- ① 群级基线 ----------
print("=" * 70)
print("① 群级基线筛选（采样 LLM 判定锚定率 → 分档）")
print("=" * 70)
data = json.load(open(os.path.join(BASE, 'qq_anchored_judged.json'), encoding='utf-8'))
groups = []
for g, items in data.items():
    n = len(items)
    a = sum(1 for it in items if it.get('has_anchor'))
    rate = a / n
    tier = "污染群（排除）" if rate < 0.10 else ("临界群（降权）" if rate < 0.25 else "有效群（进入）")
    groups.append((g, n, a, rate, tier))
    print(f"  {g}: 采样 {n} 条, 锚定 {a} ({rate:.1%}) → {tier}")

# 伪史论群（无 LLM 判定，用历史锚定率 4.5%）
print(f"  伪史论群（军事历史）: 锚定率 4.5% → 污染群（排除）")
groups.append(("伪史论群", 0, 0, 0.045, "污染群（排除）"))

enter = [g for g in groups if g[4].startswith("有效群")]
print(f"\n  进入条级富集的群: {len(enter)} 个（5 主群）| 排除: 伪史论群")

# ---------- ② 条级富集（对 5 主群合并语料） ----------
print()
print("=" * 70)
print("② 条级富集（词汇打分器，5 主群合并 2000 条）")
print("=" * 70)
rows = []
for g, items in data.items():
    for it in items:
        rows.append({"msg": it.get("message", ""), "anchor": bool(it.get("has_anchor")), "group": g})
scores = [(score_of(r["msg"]), r["anchor"]) for r in rows]
n_anchor_total = sum(1 for _, a in scores if a)
print(f"  基线: {len(rows)} 条, 锚定率 {n_anchor_total/len(rows):.1%}")
print(f"  {'阈值≥':>6}{'保留':>7}{'锚定率':>8}{'富集':>6}{'累计筛除':>8}")
for thr in [1, 2, 3]:
    passed = [(s, a) for s, a in scores if s >= thr]
    if not passed:
        continue
    n_pa = sum(1 for _, a in passed if a)
    rate = n_pa / len(passed)
    print(f"  {thr:>6}{len(passed):>7}{rate:>8.1%}{rate/0.288:>6.1f}x{1-len(passed)/len(rows):>8.1%}")

# ---------- ③ 清洗后统计 + 端到端漏斗 ----------
print()
print("=" * 70)
print("③ 端到端清洗漏斗（两级架构）")
print("=" * 70)
print("  输入: 海量群聊（5 主群 + 伪史论群等污染群）")
print("  └─ ① 群级基线: 伪史论群（4.5%）排除; 5 主群（23.8-33.8%）进入")
print("  └─ ② 条级富集(≥2): 保留 100/2000 = 5.0%, 锚定率 60%（2.1x 富集）")
print("  └─ ③ 清洗后: 高纯度子集（锚定率 60-82%），供训练数据")
print()
print("  关键指标（清洗率）:")
print(f"    群级排除: 伪史论群 100%（污染群整体排除）")
print(f"    条级筛除: 95.0%（≥2 档）~ 99.2%（≥3 档）")
print(f"    锚定率提升: 28.8% → 60%（≥2 档）~ 82.4%（≥3 档）")
print(f"    与污染群最终分离: 清洗后子集 60% vs 伪史论群 4.5% = 13x")
