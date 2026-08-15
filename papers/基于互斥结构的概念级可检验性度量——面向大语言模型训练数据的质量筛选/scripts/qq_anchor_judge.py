# -*- coding: utf-8 -*-
"""前置补齐：高参与度群评论 LLM 判定（has_anchor/stance/topic）
公开版脱敏：群名保留，群号隐去；本地路径改为环境变量/相对路径。
"""
import json, os, sys, re, time, random
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
QQ = os.environ.get("PCAVT_QQ_DIR", BASE)

def llm(prompt, max_tokens=1000):
    raise NotImplementedError(
        "公开版不内置 API Key。请设置 LLM_API_KEY 并在此实现兼容的 llm() 调用。"
    )

def extract_json(text):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if m: text = m.group(1)
    i, j = text.find("{"), text.rfind("}")
    if i >= 0 and j > i: text = text[i:j+1]
    return json.loads(text)

GROUPS = {
    "后花园三号": os.environ.get("QQ_GROUP_ID_后花园三号", "REDACTED"),
    "8号病栋": os.environ.get("QQ_GROUP_ID_8号病栋", "REDACTED"),
    "9号病栋": os.environ.get("QQ_GROUP_ID_9号病栋", "REDACTED"),
    "非正常人类": os.environ.get("QQ_GROUP_ID_非正常人类", "REDACTED"),
    "后花园四号": os.environ.get("QQ_GROUP_ID_后花园四号", "REDACTED"),
}
KEYWORDS = ["女权", "女拳", "共产", "体制", "分配", "平等", "资本家", "剥削", "键政",
            "改革开放", "经济", "文", "理", "LGBT", "华为", "小米", "游戏", "AI",
            "道德", "教育", "历史", "司法", "未成年", "游行", "台湾", "种族"]

def judge(item):
    msg = item["text"][:250]
    prompt = f"""你是评论区分析师。QQ群讨论中有一条评论：
评论：{msg}

任务：判定「锚定状态」和「争议性」。
【锚定定义】有锚 = 包含可检验内容（具体事实/数据/案例/个人经历/逻辑论证）；无锚 = 纯立场/情绪/玩梗/谩骂/无依据断言。

输出 JSON：
{{"has_anchor": true/false, "anchor_evidence": "锚定证据（无则空）",
 "is_dispute": true/false, "stance": "立场（30字内）",
 "topic": "话题（经济/文理科/性别/科技/游戏/政治/历史/其他）"}}"""
    out = llm(prompt, max_tokens=1000)
    try:
        r = extract_json(out)
    except Exception as e:
        r = {"has_anchor": None, "error": str(e)[:60]}
    r["message"] = msg[:120]
    return r

all_data = {}
for gname, gid in GROUPS.items():
    path = os.path.join(QQ, f"group_{gid}.jsonl")
    texts = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            d = json.loads(ln)
            t = (d.get("text") or "").strip()
            if 10 <= len(t) <= 200:
                texts.append(t)
    # 争议词优先采样 400
    random.seed(42)
    kw_hits = [t for t in texts if any(k in t for k in KEYWORDS)]
    rest = [t for t in texts if t not in kw_hits]
    random.shuffle(kw_hits); random.shuffle(rest)
    sample = kw_hits[:250] + rest[:150]
    print(f"{gname}: 共{len(texts)}条, 采样{len(sample)}（争议词优先{len(kw_hits[:250])}）", flush=True)

    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(judge, {"text": t}): t for t in sample}
        for fut in as_completed(futs):
            r = fut.result()
            r["group"] = gname
            results.append(r)
            done += 1
            if done % 100 == 0:
                print(f"  {gname} {done}/{len(sample)}", flush=True)

    anchored = [r for r in results if r.get("has_anchor") is True]
    print(f"  → 有锚 {len(anchored)}/{len(results)} ({len(anchored)/len(results)*100:.1f}%)", flush=True)
    all_data[gname] = results

with open(os.path.join(BASE, "qq_anchored_judged.json"), "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print("\n已存 qq_anchored_judged.json", flush=True)
