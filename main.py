import numpy as np
import math

v = []
f = []
n = []
c = []
S = []
v_f = {}

# 读取obj
obj = open("noise.obj")
line = obj.readline()
while line:
    if line.startswith("v"):
        v.append(line[1:].split())
    elif line.startswith("f"):
        f.append(line[1:].split())
    # print(line, end = '')　　　
    line = obj.readline()

obj.close()
# list转numpy
vv = np.array(v, float)
ff = np.array(f, int)

# 计算法向量、重心、面积
for i in range(len(ff)):
    normal = np.cross(vv[ff[i][1] - 1] - vv[ff[i][0] - 1], vv[ff[i][2] - 1] - vv[ff[i][1] - 1])
    # 利用叉乘以求面积
    Area = np.linalg.norm(normal)/2
    normal /= np.linalg.norm(normal)
    n.append(normal)
    S.append(Area)
    center = (vv[ff[i][0] - 1] + vv[ff[i][1] - 1] + vv[ff[i][2] - 1])/3
    c.append(center)
nn = np.array(n)
SS = np.array(S)
cc = np.array(c)


# 计算点的相关面（为后续获得每个面的1-ring面做准备）
for i in range(len(vv)):
    v_f[i+1] = []
for i in range(len(ff)):
    # print(ff[i][0])
    v_f[ff[i][0]].append(i)
    v_f[ff[i][1]].append(i)
    v_f[ff[i][2]].append(i)

def get_one_ring(fi):
    # 获得每个面的1-ring面
    v1 = ff[fi][0]
    v2 = ff[fi][1]
    v3 = ff[fi][2]
    res = list(set(v_f[v1] + v_f[v2] + v_f[v3]))
    return res

# 计算相邻面之间的平均距离和平均法向量差值
e_num = 0
total_distance = 0.0
n_distance = 0.0
for i in range(len(ff)):
    near = get_one_ring(i)
    e_num += len(near)
    for j in near:
        total_distance += np.linalg.norm(cc[i]-cc[j])
        n_distance += np.linalg.norm(nn[i]-nn[j])
avg_distance = total_distance/e_num
avg_n_distance = n_distance/e_num
avg_distance **= 2
avg_n_distance **= 2

# 计算相邻面之间法向量的差值


def weight_s(ci, cj):
    global vv, nn, cc, SS
    distance = np.linalg.norm(cc[ci] - cc[cj])
    distance **= 2
    return math.exp(-0.5 * distance/avg_distance)

def weight_r(ni, nj):
    global vv, nn, cc, SS
    n_distance = np.linalg.norm(nn[ni] - nn[nj])
    n_distance **= 2
    return math.exp(-0.5 * n_distance/avg_n_distance)

def update_normal():
    global vv, nn, cc, SS
    new_n = []
    for x in range(len(ff)):
        Kp = 0.0
        total = 0.0
        one_ring = get_one_ring(x)
        for y in range(len(one_ring)):
            Kp += SS[one_ring[y]]*weight_s(x, one_ring[y])*weight_r(x, one_ring[y])
            total += SS[one_ring[y]]*weight_s(x, one_ring[y])*weight_r(x, one_ring[y])*nn[one_ring[y]]
        new_n.append(total/Kp)
    nn = np.array(new_n)

def update_point():
    global vv, nn, cc, SS
    new_v = []
    for x in range(len(vv)):
        total = np.array([0.0, 0.0, 0.0])
        near_f = v_f[x+1]
        for y in range(len(near_f)):
            total += nn[near_f[y]]*(np.dot(nn[near_f[y]], (cc[near_f[y]] - vv[x])))
        new_v.append(vv[x] + total/len(near_f))
    # 更新点
    vv = np.array(new_v)

    # 点更新后重新计算每个面的重心
    temp_c = []
    for x in range(len(ff)):
        center = (vv[ff[x][0] - 1] + vv[ff[x][1] - 1] + vv[ff[x][2] - 1]) / 3
        temp_c.append(center)
    cc = np.array(temp_c)


if __name__ == '__main__':
    for i in range(5):
        update_normal()
    for i in range(10):
        update_point()
        noise_obj = open("output_" + str(i+1)+".obj", "w")
        for i in range(len(vv)):
            noise_obj.write('v ' + str(vv[i])[1:-1] + '\n')
        for i in range(len(ff)):
            noise_obj.write('f ' + str(ff[i])[1:-1] + '\n')
        noise_obj.close()







