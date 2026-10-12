"""
    贪心算法实现（思想：来了就选空闲的充电设备中最优的那个充电）
    需要输入：监测周期，无人机集合，充电器集合
    输出：规划，总监测效用
"""
import time

import numpy as np
from utils.Utils import Utils
import networkx as nx
from utils.KM import KM


class GA(object):

    def __init__(self, T, V, L):
        # 初始化决策变量x_ikq
        self.decisons = np.zeros((T + 1, len(V), len(L)), dtype=int)
        # 初始化感知效用的值
        self.U_arr = np.zeros(T + 1)
        self.U = 0.0
        L_occupy = np.zeros((T + 1, len(L)), dtype=int)  # 0-空闲，1-占用中
        V_arrival = np.zeros((T + 1, len(V)), dtype=int)  # 0-待分配，1-无法分配
        for q in range(1, T + 1):
            V_new = []
            L_new = []
            for v in V:
                if V_arrival[q, v.name] == 0:
                    V_new.append(v)
            for l in L:
                if L_occupy[q, l.name] == 0:
                    L_new.append(l)
            if len(V_new) > 0 and len(L_new) > 0:
                # 构建二分图(V-L,E=V-L,边权值为U_ikq)
                G = Utils.construct_bipartite_graph(Utils(), V_new, L_new, q, T)
                # 最大权二分图匹配
                V_set, L_set = nx.bipartite.sets(G)
                n, m = len(V_set), len(L_set)
                # 定义权重矩阵
                weight = np.zeros((n, m))
                for i, v in enumerate(V_set):
                    for j, l in enumerate(L_set):
                        if G.has_edge(v, l):
                            weight[i][j] = G[v][l]['weight']
                km = KM()
                # KM算法求出最优匹配，这个匹配有bug，可能会死循环
                max_ = km.compute(weight)
                for i in max_:
                    if i[1] != -1 and weight[i[0], i[1]] > 0:
                        self.U += weight[i[0], i[1]]
                        # 这里需要处理
                        v_result = int(list(V_set)[i[0]][-1])
                        l_result = int(list(L_set)[i[1]][-1])
                        self.decisons[q][v_result][l_result] = 1
                        v = V[v_result]
                        charge_time, charge_utility = Utils.compute_charge_i_k_q(Utils(), v, L[l_result], q, T)
                        for t in range(q, q + 2 * v.travel_time + v.work_time + charge_time):
                            if t > T:
                                continue
                            V_arrival[t, v_result] = 1  # 无人机被分配成功，这段时间都不能再次被分配
                        for h in range(q, q + charge_time):
                            if h > T:
                                continue
                            L_occupy[h, l_result] = 1  # 充电设备被分配成功，这段时间都不能再次被分配
            self.U_arr[q] = self.U
