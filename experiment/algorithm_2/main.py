"""
    实验核心代码
"""
from experiment.algorithm_1.Generate_System import Generate_System
from experiment.algorithm_2.Lyapunov import Lyapunov

length = 10  # 平面区域边长（单位：米）
m = 50  # 兴趣点数量
n = 3  # 无人机数量
z = 2  # 充电器数量
charge_power_list = [1, 2]  # 充电器功率列表
charge_pricie_list = [1, 3]  # 充电器充电单价列表
work_power_list = [1.5, 1.9, 2.5]  # 无人机工作功率列表
e_max_list = [1.9, 6.5, 5.1]  # 无人机电池容量列表
e_min_list = [1, 1, 1]  # 无人机可工作的最小电量列表
energy_consumption_list = [0.5, 0.7, 0.8]  # 无人机往返充电站的能耗量列表
speed_list = [1, 1, 1]  # 无人机飞行速度列表
sense_range_list = [1, 1, 5]  # 无人机监测范围列表
effect = 10  # 监测价值影响因子（需要确保价值可以大于充电成本），可以理解为给每个POI的权重系数乘了effect
T = 100  # 系统周期为T个时隙
W = 10  # 目标函数对漂移函数的惩罚权值
r = 10  # 充电成本上限
tao = 7  # 时隙间隔，影响每个充电器的服务时长

if __name__ == '__main__':
    # 生成模型
    system = Generate_System(length, m, charge_power_list, charge_pricie_list,
                             work_power_list, e_max_list, e_min_list, energy_consumption_list,
                             speed_list, sense_range_list, effect)
    V = system.V  # 无人机集合
    L = system.CS.L  # 充电器集合
    print("###################################以下为李雅普诺夫算法###########################################")
    result_1 = Lyapunov(T, V, L, W, r, tao)
    for q in range(1, T + 1):
        print("在时隙", q, "总共有", result_1.V_q_num[q], "个无人机")
        for i in range(len(V)):
            for k in range(len(L)):
                if result_1.decisons[q][i][k] != 0:
                    print("v_", i, "在时隙", q, "选择l_", k, "进行充电")
        print("在时隙", q, "所能获得的最大总感知价值为：", result_1.Q_arr[q])
    # 输出图像

    ###################################以下为对比算法###########################################
    # 调用algorithm1的GA算法再跑一遍即可，差值的不用动，比值的将Utils.compute_charge_i_k_q中的charge_utility修改为比值即可
