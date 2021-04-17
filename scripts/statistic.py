# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 21:25:00 2021

@author: Chang
"""
import random
import matplotlib.pyplot as plt

def pie_draw_n(pct, allvals, txt):
    absolute = round(pct/100.*np.sum(allvals))
    return_txt = ""
    if txt == "all":
        return_txt = "{:.1f}%\n({:})".format(pct, absolute)
    elif txt == "per":
        return_txt = "{:.1f}%".format(pct)
    else:
        return_txt = "{:.1f}%\n({:})".format(pct, absolute)
    return return_txt

def bar_autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{:.1f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


s1 = [1,2,3,4,5]
s2 = [1,3,5]

num_s1 = [0]*5
num_s2 = [0]*3
num = [0]*26
x_val = [0, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

for i in range (1000000):
    x1 = random.randint(1,5)
    y1 = random.randint(0,2)
    val = (x1)*(s2[y1])

    num[val] +=1
    
fig, ax = plt.subplots()
rects = ax.bar(x_val, num)
bar_autolabel(rects)
plt.show()