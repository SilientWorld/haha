"""
    工具类
    1.计算时隙q下v_i在l_k的充电时长和充电效用
    2.构建二分图(V-L,E=V-L,边权值为U_ikq)
"""
import math
import networkx as nx
import numpy as np


class Utils(object):

    # 计算时隙q下v_i在l_k的充电时长和充电效用
    def compute_charge_i_k_q(self, v_i, l_k, q, period_time):
        max_time = math.ceil(v_i.E_i / l_k.charge_power)
        if q - 1 + max_time <= period_time:
            charge_time = max_time
        else:
            charge_time = period_time - q + 1
        charge_cost = charge_time * l_k.charge_pricie
        if q + charge_time + v_i.work_time + 2 * v_i.travel_time - 1 <= period_time:
            charge_utility = float(format(v_i.Q_i - charge_cost, '.2f'))
            # 第二个点的对比算法中比值算法要用到
            # charge_utility = float(format(v_i.Q_i / charge_cost, '.2f'))
        else:
            charge_utility = -charge_cost
        return charge_time, charge_utility

    # 构建二分图(V-L,E=V-L,边权值为U_ikq)
    def construct_bipartite_graph(self, V, L, t, b):
        # 初始化一个空图
        G = nx.Graph()

        # 添加左部顶点，即无人机
        for i in range(len(V)):
            G.add_node("v_" + str(V[i].name), bipartite=0)

        # 添加右部顶点，即充电站
        for k in range(len(L)):
            G.add_node("l_" + str(L[k].name), bipartite=1)

        # 添加无人机和充电站之间的边，这里需要修改：并不是从t到b，而是从v_i可以分配到l_k的时隙到b(todo)
        for i in range(len(V)):
            for k in range(len(L)):
                charge_time, charge_utility = Utils.compute_charge_i_k_q(Utils(), V[i], L[k], t, b)
                if charge_utility < 0:
                    charge_utility = 0.0  # 为了便于使用KM算法
                G.add_edge("v_" + str(V[i].name), "l_" + str(L[k].name),
                           weight=charge_utility)
        # print(nx.get_edge_attributes(G, 'weight'))
        return G

    # 构建二分图(V-L,E=V-L,边权值为U_ikq)
    def construct_bipartite_graph_new(self, V, L, b, L_occupy, V_arrival):
        # 初始化一个空图
        G = nx.Graph()
        # 每一个v_i可以分配到l_k的最早时隙
        V_L_last_free_arr = np.zeros((len(V), len(L)), dtype=int)
        # 充电时间集合
        V_L_charge_time_arr = np.zeros((len(V), len(L)), dtype=int)

        # 添加左部顶点，即无人机
        for i in range(len(V)):
            G.add_node("v_" + str(V[i].name), bipartite=0)

        # 添加右部顶点，即充电站
        for k in range(len(L)):
            G.add_node("l_" + str(L[k].name), bipartite=1)

        # 添加无人机和充电站之间的边，这里需要修改：并不是从t到b，而是从v_i可以分配到l_k的时隙到b
        for i in range(len(V)):
            for k in range(len(L)):
                # 计算v_i可以分配到l_k的最早时隙t
                v_i_last_free = 1
                l_k_last_free = 1
                for x in range(b, 0, -1):
                    if V_arrival[x][i] == 1:
                        v_i_last_free = x + 1
                        break
                for y in range(b, 0, -1):
                    if L_occupy[y][k] == 1:
                        l_k_last_free = y + 1
                        break
                t = max(v_i_last_free, l_k_last_free)
                V_L_last_free_arr[i][k] = t
                charge_time, charge_utility = Utils.compute_charge_i_k_q(Utils(), V[i], L[k], t, b)
                V_L_charge_time_arr[i][k] = charge_time
                if charge_utility < 0:
                    charge_utility = 0.0  # 为了便于使用KM算法
                G.add_edge("v_" + str(V[i].name), "l_" + str(L[k].name),
                           weight=charge_utility)
        return G, V_L_last_free_arr, V_L_charge_time_arr
# if __name__ == '__main__':
#     # print(Utils.compute_charge_i_k_q(Utils(), V[0], L[0], 1, T))
#     G = nx.Graph()
#
#     G.add_nodes_from(['A', 'B', 'C', 'D'])
#     G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A'), ('A', 'C')])
#
#     nx.draw(G, with_labels=True)
#     plt.show(block=True)
