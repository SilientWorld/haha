"""
    启发式算法实现（等所有无人机都到了一起分配
    需要输入：监测周期，无人机集合，充电器集合
    输出：规划，总监测效用
"""
from utils.KM import KM
from utils.Utils import Utils
import numpy as np
import networkx as nx



class Qifashi(object):

    def __init__(self, T, V, L):
        phi = np.iinfo(np.int32).min
        mu = np.iinfo(np.int32).max
        # 计算最大值phi和最小值mu
        for q in range(1, T + 1):
            for v_i in V:
                for l_k in L:
                    charge_time, charge_utility = Utils.compute_charge_i_k_q(Utils(), v_i, l_k, q, T)
                    phi = max(phi, charge_time + 2 * v_i.travel_time + v_i.work_time)
                    mu = min(mu, charge_time + 2 * v_i.travel_time + v_i.work_time)
        # 初始化决策变量x_ikq
        self.decisons = np.zeros((T + 1, T + 1, len(V), len(L)), dtype=int)
        # 初始化感知效用的值
        self.U_arr = np.zeros(T + 1)
        for b in range(mu + 1, T + 1):
            t_opt = 0
            M_opt = []
            for t in range(1, b+1):
                # 构建二分图(V-L,E=V-L,边权值为U_ikq)
                G = Utils.construct_bipartite_graph(Utils(), V, L, b - t + 1, b)
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
                max_ = km.compute(weight)
                match = []
                F = 0
                for i in max_:
                    if i[1] != -1 and weight[i[0], i[1]] > 0:
                        match.append([int(list(V_set)[i[0]][-1]), int(list(L_set)[i[1]][-1])])
                        F += weight[i[0], i[1]]
                # print("最大匹配：", match, ";", "最大效用为：", F)

                # 更新前b个时隙的最优解
                if self.U_arr[b-t] + F > self.U_arr[b]:
                    t_opt = t
                    M_opt = match
                    self.U_arr[b] = self.U_arr[b-t] + F
                # print("最大组合:", max_, weight[[i[0] for i in max_], [i[1] for i in max_]])
            # print(b)
            # print("最佳时隙：", t_opt)
            # print("最佳匹配：", M_opt)
            self.decisons[b] = self.decisons[b-t_opt]
            if len(M_opt) > 0:
                for p in range(b - t_opt + 1, b + 1):
                    self.decisons[b][p].fill(0)
                for m in M_opt:
                    self.decisons[b][b-t_opt+1][m[0]][m[1]] = 1
        # print(self.decisons)

