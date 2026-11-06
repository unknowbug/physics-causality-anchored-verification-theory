# -*- coding: utf-8 -*-
"""快速过滤器拒绝能力测试：无锚群（伪史论讨论群）语料 vs 5 主群
公开版脱敏：群名保留，群号隐去；本地路径改为环境变量/相对路径。
"""
import json, io, sys, re, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
PSEUDO_GROUP_ID = os.environ.get("QQ_GROUP_ID_PSEUDOHISTORY", "REDACTED")
SAMPLE = os.environ.get(
    "PCAVT_PSEUDO_SAMPLE",
    os.path.join(BASE, "jsonl_samples", f"group_{PSEUDO_GROUP_ID}.jsonl"),
)

# 与 v1.0 相同的特征定义
POS = ["数字", "量化单位", "条件句", "因果词", "引证", "具体时间"]
NEG = ["绝对化", "情绪词", "反问感叹", "身份标签", "长度过短", "长度过长"]

def feats(msg):
    m = msg or ""
    f = {}
    f["数字"] = bool(re.search(r'\d', m))
    f["量化单位"] = bool(re.search(r'\d+\s*(万|亿|元|块|年|月|日|次|倍|%|％|个|条|人|张|台|款|亿|万亿)', m))
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

# 加载伪史论群消息
msgs = []
if PSEUDO_GROUP_ID != "REDACTED" and os.path.exists(SAMPLE):
    with open(SAMPLE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            txt = None
            for k in ("message", "content", "msg", "text"):
                if isinstance(obj, dict) and obj.get(k):
                    txt = obj[k]
                    break
            if not txt:
                continue
            msgs.append(str(txt))
print(f"伪史论群消息数: {len(msgs)}")
if not msgs:
    print("[公开版] 未提供伪史论群数据文件，跳过对照。")
    raise SystemExit(0)

scores = [score_of(m) for m in msgs]
dist = Counter(scores)
print("\n打分分布（伪史论群 vs 5 主群对照）:")
print(f"{'分数':>4}{'伪史论群':>10}{'比例':>8}")

# 5 主群打分分布（对照）
data = json.load(open(os.path.join(BASE, 'qq_anchored_judged.json'), encoding='utf-8'))
main_scores = []
for g, items in data.items():
    for it in items:
        main_scores.append(score_of(it.get("message", "")))
main_dist = Counter(main_scores)
total_main = len(main_scores)

print(f"{'分数':>4}{'伪史论':>8}{'伪史论%':>8}{'5主群':>8}{'5主群%':>8}")
for s in range(-3, 5):
    ph = dist.get(s, 0)
    mn = main_dist.get(s, 0)
    print(f"{s:>4}{ph:>8}{ph/len(msgs)*100:>8.1f}{mn:>8}{mn/total_main*100:>8.1f}")

# 严格档对比：≥2 放行率
ph2 = sum(1 for s in scores if s >= 2) / len(msgs)
mn2 = sum(1 for s in main_scores if s >= 2) / total_main
ph3 = sum(1 for s in scores if s >= 3) / len(msgs)
mn3 = sum(1 for s in main_scores if s >= 3) / total_main
print(f"\n阈值≥2 放行率: 伪史论群 {ph2:.3f} vs 5主群 {mn2:.3f} (比值 {mn2/max(ph2,1e-6):.1f}x)")
print(f"阈值≥3 放行率: 伪史论群 {ph3:.3f} vs 5主群 {mn3:.3f} (比值 {mn3/max(ph3,1e-6):.1f}x)")
