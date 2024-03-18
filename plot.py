import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

def create_plot(dataf,plot_window):
    # 读取CSV文件数据,写个if，latep==''时只画俩图
    plt.rcParams['font.sans-serif'] = ['SimHei']
    name = dataf.iloc[0, 0]
    total = dataf.iloc[0, 1]
    totalp = dataf.iloc[0, 2]
    latep = dataf.iloc[0, 4]
    earlyp = dataf.iloc[0, 6]
    try:
        zerop = 1 - earlyp - latep
    except:
        zerop = ''
    mean = dataf.iloc[0, 7]
    wcz = dataf.iloc[0, 8:27]
    wcz = wcz.astype(float).round().astype(int)
    wczp = dataf.iloc[0, 27:46]
    wczpp = wczp*100

    wcz = wcz[::-1]
    wczp = wczp[::-1]
    wczpp = wczpp[::-1]

    # 创建Matplotlib图形
    fig = plt.Figure(figsize=(8, 6))

    # 饼图1
    ax1 = fig.add_subplot(221)
    ax1.pie([totalp, 1-totalp], labels=['符合标准比例', '不符合标准比例'], autopct='%1.1f%%', startangle=90)
    ax1.set_title(f'{name}\n样本总数：{total}')

    # 饼图2
    if earlyp != '':
        ax2 = fig.add_subplot(222)
        def my_autopct(pct):
            return f'{pct:.1f}%' if pct != 0 and pct != zerop else ''
        ax2.pie([latep, earlyp, zerop], labels=['晚于基准字段的比例', '早于基准字段的比例', ''], autopct=my_autopct,
                startangle=90)
        ax2.set_title(f'早晚基准字段的数据比例')

    # 柱状图
    ax3 = fig.add_subplot(212)
    labels = [f'{5*(i+1)}%位次值: {data}' for i, data in enumerate(wcz)]
    ax3.bar(labels, wczp, color='skyblue')
    ax3.set_title(f'{name}_位次值分布，平均值：{mean:.3f}')
    ax3.set_yticks(np.arange(0, 1.01, 0.2))
    # 设置纵坐标轴范围为0%到100%
    ax3.set_ylim(0, 1)
    ax3.yaxis.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    # 在每个柱子上方添加值的标注
    for bar, value in zip(ax3.patches, wczpp):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2, height, f'{value:.2f}%',
                 ha='center', va='bottom', fontsize=8)

    # 调整横坐标标签文字大小
    plt.setp(ax3.get_xticklabels(), rotation=45, ha="right", fontsize=8)

    # 调整布局
    fig.tight_layout()

    # 将Matplotlib图形嵌入Tkinter窗口
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
