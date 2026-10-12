"""
    Lyapunov算法实现
    需要输入：监测周期，无人机集合，充电器集合，目标函数对漂移函数的惩罚权值，充电成本上限，时隙间隔
    输出：规划，总监测效用
"""
import math

import numpy as np
import random

from experiment.algorithm_2.GAP import GAP


class Lyapunov(object):

    def __init__(self, T, V, L, W, r, tao):
        # 队列函数
        self.I_arr = np.zeros(T + 1)
        # 初始化决策变量x_ikq
        self.decisons = np.zeros((T + 1, len(V), len(L)), dtype=int)
        # 初始化感知效用的值
        self.Q_arr = np.zeros(T + 1)
        # 初始化时隙q的无人机集合数量
        self.V_q_num = np.zeros(T + 1, dtype=int)

        for q in range(1, T + 1):
            # 从V中随机选取元素组成V_q
            self.V_q_num[q] = random.randint(0, len(V))
            V_q = random.sample(V, self.V_q_num[q])
            I_q = self.I_arr[q]
            # v_i在l_k充电可获得的收益，默认都是正的
            profit_arrs = np.zeros((len(V), len(L)), dtype=float)
            # v_i在l_k充电产生的成本，默认都是正的
            cost_arrs = np.zeros((len(V), len(L)), dtype=float)
            # v_i在l_k充电占用的时隙数，默认都是整数
            charge_time_arrs = np.zeros((len(V), len(L)), dtype=int)
            # 更新所有组合对应的收益
            for v in V_q:
                for l in L:
                    charge_time_arrs[v.name][l.name] = math.ceil(v.E_i / l.charge_power)
                    cost_arrs[v.name][l.name] = charge_time_arrs[v.name][l.name] * l.charge_pricie
                    profit_arrs[v.name][l.name] = float(
                        format(W * v.Q_i - (I_q - r) * cost_arrs[v.name][l.name], '.2f'))
            # print(profit_arrs)

            # 调用GAP算法求解最大分配方案
            match = []
            if len(V_q) > 0:
                match = GAP(V_q, L, profit_arrs, tao, charge_time_arrs).next_bin()
            # print(match)
            if len(match) > 0:
                for o in range(len(L)):
                    m = match[o]
                    if len(m) > 0:
                        for i in m:
                            self.decisons[q][V_q[i].name][o] = 1

            # 根据解更新所花费的总充电成本和监测价值
            total_cost = 0
            for i in range(len(V)):
                for k in range(len(L)):
                    if self.decisons[q][i][k] == 1:
                        total_cost += cost_arrs[i][k]
                        self.Q_arr[q] += V[i].Q_i
            if q < T:
                self.I_arr[q + 1] = max(I_q + total_cost - r, 0)
