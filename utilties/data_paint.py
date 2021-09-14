#!/usr/bin/env python
# coding=utf-8

import matplotlib.pyplot as plt   # Python画图工具
from matplotlib.gridspec import GridSpec     # 利用网格确定图形的位置
import matplotlib
print(matplotlib.matplotlib_fname())
fig = plt.figure(figsize=(20, 20))
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用于显示中文
plt.rcParams['axes.unicode_minus'] = False  # 用于显示中文

# plt.rcParams['font.sans-serif']=['Times New Roman']

fig.suptitle('sex', fontsize=30, x=0.5, y=0.93)

gs = GridSpec(40, 40)

# 第一个子图
# ax1是axes对象，这一步意思是ax1画的图在原图(40*40)占据行5-14，占据列5-14(从零开始索引)
ax1 = fig.add_subplot(gs[5:10, 5:25])
sex = ['Male', 'Female']
colors = ['red', 'yellow']
data = [128, 445]

# 为横条设置标签
b = ax1.barh(range(len(sex)), data, tick_label=sex, color=colors)
for rect in b:
    w = rect.get_width()
    plt.text(w, rect.get_y() + rect.get_height()/2, '%d ' %
             int(w), ha='left', va='center', fontsize='15')
ax1.set_yticks(range(len(sex)))
ax1.set_yticklabels(sex, fontsize=15, font="Monaco")
ax1.set_xticks(())
ax1.set_title('水平横向的柱状图', loc='center', fontsize='20',
              fontweight='bold', color='red', x=0.5, y=1.22)
# 第二个子图
# ax2画的图在原图(40*40)占据行20-39，占据列20-39(从零开始索引)
ax2 = fig.add_subplot(gs[:12, 27:])
colors = ['pink', 'green']
ax2.set_title('饼图', fontsize=20, x=0.5, y=1.02)
patches, l_text, p_text = ax2.pie(data,
                                  explode=(0, 0.03),
                                  labels=sex,
                                  colors=colors,
                                  autopct='%3.2f%%',  # 数值保留固定小数位
                                  shadow=False,  # 无阴影设置
                                  startangle=90,  # 逆时针起始角度设置
                                  pctdistance=0.6)  # 数值距圆心半径倍数的距离

# 改变饼图文本的大小
# 方法是把每一个text遍历。调用set_size方法设置它的属性
for t in l_text:
    t.set_size(15)
for t in p_text:
    t.set_size(15)
# 设置x，y轴刻度一致，这样饼图才能是圆的
plt.axis('equal')
plt.show()
