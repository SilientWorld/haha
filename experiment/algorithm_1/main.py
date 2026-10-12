"""
    实验核心代码
"""
import time
import numpy as np
import pandas as pd

from experiment.algorithm_1.Qifashi import Qifashi
from experiment.algorithm_1.UDCSA_new import UDCSA_new
from experiment.algorithm_1.Generate_System import Generate_System
from experiment.algorithm_1.GA import GA

length = 10  # 平面区域边长（单位：米）
m = 100  # 兴趣点数量
n = 50  # 无人机数量
z = 20  # 充电器数量
charge_power_list = [1, 2]  # 充电器功率列表
charge_pricie_list = [1, 3]  # 充电器充电单价列表
work_power_list = [1.5, 1.9, 2.5]  # 无人机工作功率列表
e_max_list = [1.9, 6.5, 5.1]  # 无人机电池容量列表
e_min_list = [1, 1, 1]  # 无人机可工作的最小电量列表
energy_consumption_list = [0.5, 0.7, 0.8]  # 无人机往返充电站的能耗量列表
speed_list = [1, 1, 1]  # 无人机飞行速度列表
sense_range_list = [1, 2, 5]  # 无人机监测范围列表
effect = 0.1  # 监测价值影响因子（需要确保价值可以大于充电成本），可以理解为给每个POI的权重系数乘了effect
T = 50  # 系统周期为T个时隙

if __name__ == '__main__':
    T = 20
    for i in range(1, 9):
        T += 10
        # 随机参数
        charge_power_list = np.random.randint(1, 3, size=z)
        charge_pricie_list = np.random.randint(1, 3, size=z)
        work_power_list = np.random.randint(1, 3, size=n)
        e_max_list = np.random.randint(2, 10, size=n)
        e_min_list = np.ones(n)
        energy_consumption_list = np.random.randint(1, 3, size=n)
        speed_list = np.ones(n)
        sense_range_list = np.random.randint(1, 3, size=n)
        # 生成模型
        system = Generate_System(length, m, charge_power_list, charge_pricie_list,
                                 work_power_list, e_max_list, e_min_list, energy_consumption_list,
                                 speed_list, sense_range_list, effect)
        V = system.V  # 无人机集合
        L = system.CS.L  # 充电器集合
        print("T:", T)
        print("###################################以下为UDCSA###########################################")
        start_time = time.time()  # 程序开始时间
        result_1 = GA(T, V, L)
        print("最大总感知效用为：", result_1.U_arr[T])
        # for t in range(1, T + 1):
        #     for i in range(len(V)):
        #         for k in range(len(L)):
        #             if result_1.decisons[t][i][k] != 0:
        #                 print("v_", i, "在时隙", t, "选择l_", k, "进行充电")
        end_time = time.time()  # 程序结束时间
        print("程序耗时：", end_time - start_time)
        # n = 0
        # for i in range(1, 11):
        #     print(result_1.U_arr[n])
        #     n += 10

        print("###################################以下为GA###########################################")
        start_time = time.time()  # 程序开始时间
        result_2 = UDCSA_new(T, V, L)
        print("最大总感知效用为：", result_2.U_arr[T])
        # # for t in range(1, T + 1):
        # #     for i in range(len(V)):
        # #         for k in range(len(L)):
        # #             if result_2.decisons[T][t][i][k] != 0:
        # #                 print("v_", i, "在时隙", t, "选择l_", k, "进行充电")
        end_time = time.time()  # 程序结束时间
        print("程序耗时：", end_time - start_time)
        # #
        # #
        # # # n = 0
        # # # for i in range(1, 11):
        # # #     print(result_2.U_arr[n])
        # # #     n += 10
        # #
        print("###################################以下为GTBA/Random###########################################")
        start_time = time.time()  # 程序开始时间
        result_3 = Qifashi(T, V, L)
        print("最大总感知效用为：", result_3.U_arr[T])
        # # for t in range(1, T + 1):
        # #     for i in range(len(V)):
        # #         for k in range(len(L)):
        # #             if result_3.decisons[T][t][i][k] != 0:
        # #                 print("v_", i, "在时隙", t, "选择l_", k, "进行充电")
        end_time = time.time()  # 程序结束时间
        print(end_time - start_time)



# print("###################################以下为暴力破解###########################################")
# start_time = time.time()  # 程序开始时间
# result_4 = Brute_force(T, V, L)
# # for t in range(1, T + 1):
# #     for i in range(len(V)):
# #         for k in range(len(L)):
# #             if result_4.decisons[T][t][i][k] != 0:
# #                 print("v_", i, "在时隙", t, "选择l_", k, "进行充电")
# # print("最大总感知效用为：", result_4.U_arr[T])
# end_time = time.time()  # 程序结束时间
# print("程序耗时：", end_time - start_time)
# n = 0
# for i in range(1, 11):
#     print(result_4.U_arr[n])
#     n += 10

# 输出图像
