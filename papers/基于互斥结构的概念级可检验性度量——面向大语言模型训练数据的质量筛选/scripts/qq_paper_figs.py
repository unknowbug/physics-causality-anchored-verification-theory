# -*- coding: utf-8 -*-
"""论文图件 v1：5 张核心图（DS 侧数据）
figA_Δr散点：A_rate vs Δr（伪史论独占假收敛象限）
figB_双模式全景：A_rate vs M（判决着色，语料模式）
figC_敏感性热图：概念 × p* → 判决类别
figD_过滤器富集：阈值 vs 锚定率/保留率
figE_align核验：伪史论核验结果分布（DS vs GLM）
输出：figs/（工作区，成文后归档知识库）
"""
import json, io, sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.environ.get("PCAVT_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
FIG = os.environ.get("PCAVT_FIG_DIR", os.path.join(BASE, 'figs'))
os.makedirs(FIG, exist_ok=True)

for _f in ['Microsoft YaHei', 'SimHei']:
    try:
        font_manager.findfont(_f, fallback_to_default=False)
        plt.rcParams['font.sans-serif'] = [_f, 'DejaVu Sans']
        break
    except Exception:
        continue
plt.rcParams['axes.unicode_minus'] = False

# 数据
ds = json.load(open(os.path.join(BASE, 'mutex_audit_v5_6_law1_fixed.json'), encoding='utf-8'))

# ---------- figA：Δr 散点 ----------
fig, ax = plt.subplots(figsize=(8, 6))
colors = {'无锚假收敛': 'red', '无锚': 'orange', '无锚（悬空）': 'orange',
          '可裁决争议': 'green', '健康': 'blue', '低互斥/有效': 'blue',
          '互斥超临界': 'purple'}
for nm, c in ds.items():
    if not c or 'verdict' not in c:
        continue
    A = c.get('A_rate_comment', c.get('A_rate_variant_law1', 0))
    dr = c.get('delta_r')
    if dr is None:
        continue
    v = c.get('verdict')
    col = colors.get(v, 'gray')
    ax.scatter(A, dr, c=col, s=90, edgecolors='k', linewidths=0.6, zorder=3)
    label = nm.replace('西方伪史论(文献枚举)', '伪史论').replace('文献_', '').replace('（纯市场）', '').replace('（纯计划）', '')
    ax.annotate(label, (A, dr), textcoords="offset points", xytext=(6, 5), fontsize=8)
ax.axhline(0, color='gray', ls='--', lw=0.8)
ax.axvline(0.25, color='gray', ls=':', lw=0.8)
ax.set_xlabel('A_rate（评论级锚定率）')
ax.set_ylabel('Δr = r2 - r3（维度敏感性）')
ax.set_title('概念判决散点：锚定率 vs 维度敏感性（假收敛：低锚定+高敏感性，左上）')
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=col, markersize=9, label=k)
           for k, col in colors.items() if k in [c.get('verdict') for c in ds.values()]]
ax.legend(handles=handles, loc='upper left', fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'figA_deltaR_scatter.png'), dpi=150)
plt.close(fig)
print('figA 完成')

# ---------- figB：双模式全景（A_rate vs M，语料） ----------
fig, ax = plt.subplots(figsize=(8, 6))
for nm, c in ds.items():
    if not c or 'verdict' not in c or c.get('mode') == '文献' or nm == '西方伪史论(文献枚举)':
        continue
    A = c.get('A_rate_comment', c.get('A_rate', 0))
    M = c.get('M', 0)
    v = c.get('verdict')
    ax.scatter(A, M, c=colors.get(v, 'gray'), s=110, edgecolors='k', linewidths=0.6, zorder=3)
    ax.annotate(nm.replace('QQ_', '').replace('泡吧坏女孩', '纹身').replace('小米高端化', '雷军').replace('性能声称', ''), (A, M),
                textcoords="offset points", xytext=(6, 5), fontsize=8)
ax.axvline(0.25, color='gray', ls=':', lw=0.8)
ax.axhspan(7, 20, color='yellow', alpha=0.15)
ax.set_xlabel('A_rate（评论级锚定率）')
ax.set_ylabel('M（互斥边数）')
ax.set_title('语料模式判决全景：锚定率 vs 互斥度（黄色 = S7 临界区间 [7,20]）')
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'figB_panorama.png'), dpi=150)
plt.close(fig)
print('figB 完成')

# ---------- figC：敏感性热图 ----------
concepts = ['雷军', '纹身评论', '纹身弹幕', 'QQ三号', 'QQ8号', 'QQ9号', 'QQ非正常', 'QQ四号', 'CoreSwap']
A_vals = [0.600, 0.121, 0.019, 0.278, 0.355, 0.231, 0.400, 0.278, 0.250]
M_vals = [9, 9, 6, 4, 3, 3, 6, 4, 4]
pstar = [0.20, 0.25, 0.30]
grid = np.zeros((len(concepts), 3), dtype=int)
for i, A in enumerate(A_vals):
    for j, p in enumerate(pstar):
        v = 0  # 0=健康/可裁决, 1=无锚
        if A < p:
            v = 1
        if M_vals[i] >= 7 and A >= p:
            v = 2  # 可裁决争议
        grid[i, j] = v
fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(grid, cmap='RdYlBu', aspect='auto')
ax.set_xticks(range(3)); ax.set_xticklabels(['p*=0.20', 'p*=0.25', 'p*=0.30'])
ax.set_yticks(range(len(concepts))); ax.set_yticklabels(concepts)
for i in range(len(concepts)):
    for j in range(3):
        lab = {0: '健康', 1: '无锚', 2: '可裁决'}[grid[i, j]]
        ax.text(j, i, lab, ha='center', va='center', fontsize=9)
ax.set_title('p* 敏感性：判决类别随阈值变化（横条颜色变化 = 敏感）')
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'figC_sensitivity.png'), dpi=150)
plt.close(fig)
print('figC 完成')

# ---------- figD：过滤器富集曲线 ----------
thr = [-2, -1, 0, 1, 2, 3, 4]
kept = [2000, 1995, 1852, 518, 100, 17, 2]
anchor_rate = [0.288, 0.288, 0.290, 0.425, 0.600, 0.824, 0.500]
fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(thr, anchor_rate, 'o-', color='tab:red', label='放行锚定率')
ax1.axhline(0.288, color='gray', ls='--', lw=0.8, label='基线 28.8%')
ax1.set_xlabel('打分阈值（≥）')
ax1.set_ylabel('放行消息锚定率', color='tab:red')
ax1.tick_params(axis='y', labelcolor='tab:red')
ax2 = ax1.twinx()
ax2.bar(thr, [k / 2000 for k in kept], alpha=0.3, color='tab:blue', label='保留率')
ax2.set_ylabel('保留率', color='tab:blue')
ax2.tick_params(axis='y', labelcolor='tab:blue')
ax1.legend(loc='upper right', fontsize=8)
ax2.legend(loc='center right', fontsize=8)
ax1.set_title('快速过滤器：阈值 vs 锚定率/保留率（严格档富集 2-3 倍）')
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'figD_filter.png'), dpi=150)
plt.close(fig)
print('figD 完成')

# ---------- figE：伪史论核验结果分布（DS vs GLM） ----------
glm = json.load(open(os.path.join(BASE, 'mutex_audit_v6_glm52.json'), encoding='utf-8'))
def outcome_dist(card):
    dist = {'发生': 0, '不发生': 0, '未知': 0, 'error': 0}
    for v in card.get('variants', []):
        r = v.get('verify')
        if not r:
            continue
        o = r.get('factual_outcome', 'error')
        dist[o if o in dist else 'error'] += 1
    return dist
d1 = outcome_dist(ds.get('西方伪史论(文献枚举)', {}))
d2 = outcome_dist(glm.get('西方伪史论(文献枚举)', {}))
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
for ax, dist, title in [(axes[0], d1, 'deepseek（align=0.0, n=10）'), (axes[1], d2, 'GLM5.2（align=1.0, n=2）')]:
    keys = ['不发生', '发生', '未知', 'error']
    vals = [dist.get(k, 0) for k in keys]
    cols = ['tab:red', 'tab:green', 'tab:gray', 'black']
    ax.bar(keys, vals, color=cols)
    ax.set_title(title)
    ax.set_ylabel('核验变体数')
fig.suptitle('伪史论核验结果分布：预测 vs 客观结果（align 差异来源：可核验样本数不同）')
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'figE_align_verify.png'), dpi=150)
plt.close(fig)
print('figE 完成')
print(f'\n全部图件已存: {FIG}')
