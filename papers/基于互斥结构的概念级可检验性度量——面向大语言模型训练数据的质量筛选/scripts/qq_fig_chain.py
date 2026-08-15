# -*- coding: utf-8 -*-
"""补充图件：fig0 双层架构图 + figF 伪史论判决链图
输出：figs/（工作区）
"""
import io, sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
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

def box(ax, x, y, w, h, text, fc, ec='k', fs=10, lw=1.2):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec=ec, lw=lw)
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs, wrap=True)

def arrow(ax, x1, y1, x2, y2, color='k', lw=1.5, style='-|>'):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14, color=color, lw=lw)
    ax.add_patch(a)

# ================= fig0：双层架构 =================
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')

box(ax, 0.5, 5.9, 9, 0.8, '输入：概念 C + 变体源（文献/语料）', '#e8e8e8', fs=11)

box(ax, 0.5, 4.2, 5.8, 1.3, 'LLM 提取层（可消融）\n变体枚举+极性聚类 → A 锚判定\n→ θ 相位 → (事件, 预测)', '#dae8fc', fs=10)
box(ax, 6.6, 4.2, 2.9, 1.3, '外部核验层\n检验接口真实存在性\n→ align（审计非标注）', '#fff2cc', fs=9)

box(ax, 0.5, 1.9, 9, 1.8, '确定性内核（可复现，LLM 不参与判决）\n互斥图（M）→ 结构特征（N, M, μ, r, Δr, A_rate）\n→ 判决函数 D(C) → 健康度判决 + 置信度', '#d5e8d4', fs=10)

box(ax, 0.5, 0.3, 9, 1.1, '输出：无锚 / 可裁决争议 / 健康（+置信度 z）\n→ 训练数据清洗（§7）/ 社会贡献两类判断（§9.2）', '#f8cecc', fs=10)

arrow(ax, 5, 5.9, 3.4, 5.55)          # 输入→LLM层
arrow(ax, 5, 5.9, 8.0, 5.55)          # 输入→核验层
arrow(ax, 3.4, 4.2, 5.0, 3.72)        # LLM层→内核
arrow(ax, 8.0, 4.2, 7.0, 3.72)        # 核验层→内核
arrow(ax, 5.0, 1.9, 5.0, 1.42)        # 内核→输出
ax.text(5.0, 3.45, '结构化提取', ha='center', fontsize=9, color='#555')
ax.text(7.6, 3.45, '核验结果', ha='center', fontsize=9, color='#555')
ax.set_title('图 1  双层架构：LLM 是提取器，不是判决器', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'fig0_arch.png'), dpi=150)
plt.close(fig)
print('fig0 完成')

# ================= figF：伪史论判决链 =================
fig, ax = plt.subplots(figsize=(10, 6.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis('off')

box(ax, 3.4, 7.1, 3.2, 0.7, '西方伪史论（23 变体）', '#e8e8e8', fs=10)

# 第一律
box(ax, 0.4, 5.5, 4.3, 1.2, '第一律：形式可检验性\n变体级 A_rate = 0.435（10/23）\n→ 通过（形式可检验）', '#dae8fc', fs=9)
box(ax, 5.3, 5.5, 4.3, 1.2, '第一律（行为层）\n评论级 A_rate = 0.045\n→ 行为不锚定', '#fff2cc', fs=9)

# 第二律
box(ax, 0.4, 3.6, 4.3, 1.4, '第二律：接受证伪\nr = 1.000（预测方向全一致）\nalign = 0.000（10/10 被客观事实反驳）\nΔr = +0.382（升维崩塌）\n→ 假收敛（r 高 ∧ align 低）', '#f8cecc', fs=8.5)
box(ax, 5.3, 3.6, 4.3, 1.4, '第三律（静态代理）\n分离信号 +0.390\n（形式有方案、行为拒绝）\nL4 反例吸收（考古证据=伪造）\n→ 表演检验嫌疑', '#f8cecc', fs=8.5)

# 判决
box(ax, 2.2, 1.9, 5.6, 1.2, '联合判决：无锚假收敛\n“写了不认”——四层证据\n（第一律过 ∧ 第二律死 ∧ 行为层拒绝）', '#d5e8d4', fs=10)

box(ax, 2.2, 0.3, 5.6, 1.0, '社会贡献：慎信——该讨论没有检验基础\n文献模式独立验证：μ=0.009 无锚（悬空）', '#e8e8e8', fs=9)

arrow(ax, 5, 7.1, 5, 6.73)
arrow(ax, 2.55, 5.5, 2.55, 5.05)
arrow(ax, 7.45, 5.5, 7.45, 5.05)
arrow(ax, 2.55, 3.6, 4.55, 3.1)
arrow(ax, 7.45, 3.6, 5.45, 3.1)
arrow(ax, 5, 1.9, 5, 1.33)
ax.set_title('图 4  伪史论判决链：第一律通过 ≠ 概念健康（四层证据）', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'figF_chain.png'), dpi=150)
plt.close(fig)
print('figF 完成')
print(f'已存: {FIG}')
