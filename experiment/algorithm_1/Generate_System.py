"""
    生成系统
    需要输入：二维平面的边长（默认为正方形），兴趣点数量，充电器功率列表，充电器充电单价列表，
            无人机工作功率列表，无人机电池容量列表，无人机可工作的最小电量列表，无人机往返充电站的能耗量列表，
            无人机飞行速度列表，无人机监测范围列表，监测价值影响因子（需要确保价值可以大于充电成本）

    注意：充电功率、充电单价、无人机工作功率这些变量需要确定随机的范围，这个比较复杂
"""
import math

from model.ChargeStation import ChargeStation
from model.POI import POI
from model.UAV import UAV


class Generate_System(object):
    # 在length*length的平面区域随机生成n个无人机的工作地点和m个兴趣点(坐标均位于第一象限)
    def __init__(self, length, m, charge_power_list, charge_pricie_list,
                 work_power_list, e_max_list, e_min_list, energy_consumption_list,
                 speed_list, sense_range_list, effect):
        self.O = []  # 兴趣点集合O
        # 随机生成m个兴趣点
        for i in range(m):
            o_i = POI(length)
            self.O.append(o_i)
        # 在平面区域中心生成充电站及充电器列表L
        self.CS = ChargeStation(length, charge_power_list, charge_pricie_list)

        self.V = []  # 无人机集合
        n = len(work_power_list)
        # 随机生成n个无人机的工作地点
        for i in range(n):
            # 所有无人机的电池电量默认一致
            uav = UAV(length, i)
            # 计算工作时间(向上取整，因为是时隙数)
            uav.work_time = math.ceil((e_max_list[i] - e_min_list[i]) / work_power_list[i])
            # 计算v_i与充电站的距离d_i，精确到两位小数
            x = self.CS.x - uav.x
            y = self.CS.y - uav.y
            d_i = float(format(math.sqrt(x * x + y * y), '.2f'))
            # 计算飞行时间(向上取整，因为是时隙数)
            uav.travel_time = math.ceil(d_i / speed_list[i])
            # 计算v_i的充电需求量
            uav.E_i = math.ceil(float(format(e_max_list[i] - (e_min_list[i] - energy_consumption_list[i]), '.2f')))
            # 在无人机传感范围内的兴趣点全都算在里面，计算效用时按照直线距离u=w_j*k/x计算
            for o_i in self.O:
                x = uav.x - o_i.x
                y = uav.y - o_i.y
                distance = math.sqrt(x * x + y * y)
                if distance <= sense_range_list[i]:
                    if distance == 0:
                        distance = 1
                    # 单位时隙内v_i对o_j的监测价值（与距离成反比）,取两位小数近似
                    Q_ij = float(format(o_i.w_j * effect / distance, '.2f'))
                    # 计算监测价值，取两位小数近似
                    uav.Q_i += math.ceil(float(format(Q_ij * uav.work_time, '.2f')))
            self.V.append(uav)


if __name__ == '__main__':
    system = Generate_System(10, 10, [1, 2], [1, 3],
                             [1.5, 1.9, 2.5], [1.9, 6.5, 5.1], [1, 1, 1], [0.5, 0.7, 0.8],
                             [1, 1, 1], [3, 3, 3])
    print(system.V, system.O, system.CS)
