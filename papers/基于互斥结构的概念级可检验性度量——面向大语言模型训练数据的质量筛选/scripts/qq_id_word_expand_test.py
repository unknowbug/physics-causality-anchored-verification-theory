# -*- coding: utf-8 -*-
"""问题 10：身份标签特征扩样验证
目标：在伪史论群（身份化语料）上验证身份标签词的负向信号（身份表态 = 无锚倾向）
公开版脱敏：群名保留，群号隐去；不打印私聊原文；本地路径改为环境变量/相对路径。
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

# 身份标签词表（扩样：更全面的身份化表态词）
ID_WORDS = [
    '觉醒', '粉红', '小粉红', '美分', '公知', '1450', '殖人', '恨国', '走狗',
    '汉奸', '卖国', '润人', '黄皮', '支那', '五毛', '带路党', '蛙', '井蛙',
    '爱国贼', '精日', '精美', '孝子', '跪族', '慕洋犬', '战狼', '神神', '兔兔',
    '入关', '建政', '智商税', '洗脑', '被洗脑', '清醒的人', '睁眼看世界',
]

def load_ph_msgs():
    msgs = []
    if PSEUDO_GROUP_ID == "REDACTED" or not os.path.exists(SAMPLE):
        return msgs
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
            if txt:
                msgs.append(str(txt))
    return msgs

def has_id_word(m):
    for w in ID_WORDS:
        if w in m:
            return True
    return False

def main():
    # 5 主群（有锚定标注）
    data = json.load(open(os.path.join(BASE, 'qq_anchored_judged.json'), encoding='utf-8'))
    main_rows = []
    for g, items in data.items():
        for it in items:
            main_rows.append({"msg": it.get("message", ""), "anchor": bool(it.get("has_anchor"))})
    # 伪史论群
    ph = load_ph_msgs()

    print(f"5 主群: {len(main_rows)} 条 | 伪史论群: {len(ph)} 条")
    print(f"身份标签词表: {len(ID_WORDS)} 词")

    # 1) 密度对比
    m_hit = sum(1 for r in main_rows if has_id_word(r["msg"]))
    p_hit = sum(1 for m in ph if has_id_word(m))
    print(f"\n=== 身份标签词密度 ===")
    print(f"5 主群: {m_hit}/{len(main_rows)} = {m_hit/len(main_rows):.3f}")
    print(f"伪史论群: {p_hit}/{len(ph)} = {p_hit/len(ph):.3f} "
          f"({p_hit/len(ph)/(m_hit/len(main_rows) if m_hit else 1):.1f}x)")

    # 2) 5 主群内：命中身份标签 vs 未命中的锚定率
    hit_anc = sum(1 for r in main_rows if has_id_word(r["msg"]) and r["anchor"])
    miss_anc = sum(1 for r in main_rows if not has_id_word(r["msg"]) and r["anchor"])
    miss_n = len(main_rows) - m_hit
    print(f"\n=== 5 主群内：身份标签命中 vs 锚定率 ===")
    if m_hit:
        print(f"命中身份标签: {m_hit} 条, 锚定 {hit_anc} ({hit_anc/m_hit:.3f})")
    print(f"未命中: {miss_n} 条, 锚定 {miss_anc} ({miss_anc/miss_n:.3f})")
    if m_hit:
        print(f"差异: 命中 {hit_anc/m_hit:.3f} vs 未命中 {miss_anc/miss_n:.3f}")

    # 3) 公开版不打印私聊原文，仅输出命中数统计
    print(f"\n=== 伪史论群身份标签命中数 ===")
    print(f"命中 {p_hit} 条（不展示原始消息）")

if __name__ == "__main__":
    main()
