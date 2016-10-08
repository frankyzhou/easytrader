import random as rd
import matplotlib.pyplot as plt

__author__ = 'frankyzhou'


def get_maxdown(p):
    time = 0
    cur_md = 0
    px = [0, 0]
    for i in range(len(p)):
        for j in range(len(p)):
            if j > i:
                md = float(p[j] - p[i]) / p[i]
                time += 1
                if md < cur_md:
                    cur_md = md
                    px[0] = i
                    px[1] = j
    return -cur_md, px, time

def get_maxdown_1(p):
    cur_md = 0
    time = 0
    px = [0, 0]
    for i in range(len(p)):
        for j in range(len(p)):
            cur_mx = max(p[:i+1])
            if j > i:
                time += 1
                md = float(p[j] - cur_mx) / cur_mx
                if md < cur_md:
                    cur_md = md
                    px[0] = i
                    px[1] = j
    return cur_md, px, time


def get_maxdown_2(p):
    cur_md = 0
    time = 0
    px = [0, 0]
    cur_mx = 0
    for i in range(len(p)):
        if p[i] < cur_mx:
            continue
        else:
            cur_mx = p[i]
            for j in range(len(p)):
                if j > i:
                    if p[j] > cur_mx:
                        break
                    time += 1
                    md = float(p[j] - cur_mx) / cur_mx
                    if md < cur_md:
                        cur_md = md
                        px[0] = i
                        px[1] = j
    return cur_md, px, time


def get_maxdown_3(p):
    cur_md = 0
    time = 0
    px = [0, 0]
    cur_mx = 0
    for i in range(len(p)):
        if p[i] > cur_mx:
            cur_mx = p[i]
            px[0] = i
        time += 1
        md = float(p[i] - cur_mx) / cur_mx
        if md < cur_md:
            cur_md = md
            px[1] = i
    return cur_md, px, time

p = []
for _ in range(500):
    p.append(rd.uniform(1, 30))

md, px, time = get_maxdown(p)
md1, px1, time1 = get_maxdown_1(p)
md2, px2, time2 = get_maxdown_2(p)
md3, px3, time3 = get_maxdown_3(p)
x, y = px[0], px[1]
x1, y1 = px1[0], px[1]

# plt.scatter(x, p[x], edgecolors="red")
# plt.scatter(y, p[y], edgecolors="red")
# plt.scatter(x1, p[x1])
# plt.scatter(y1, p[y1])
print time, time1, time2, time3
print px, px1, px2, px3
print md, md1, md2, md3
plt.plot(p)
plt.show()
