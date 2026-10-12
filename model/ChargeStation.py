"""
    生成充电站模型
    输入：二维平面边长，充电功率列表，充电单价列表
"""
from model.Charger import Charger


class ChargeStation(object):

    # 充电站位于在length*length平面区域正中心
    def __init__(self, length, charge_power_list, charge_pricie_list):
        self.x = length / 2  # CS的横坐标
        self.y = length / 2  # CS的纵坐标
        self.L = []  # CS的充电器列表
        z = len(charge_power_list)  # 充电器数量

        # 随机生成z个充电器
        for i in range(z):
            l_i = Charger(i)
            l_i.charge_power = charge_power_list[i]  # 充电器的充电功率
            l_i.charge_pricie = charge_pricie_list[i]  # 充电器的充电单价
            self.L.append(l_i)


if __name__ == '__main__':
    cs = ChargeStation(10, [3, 2, 1], [1, 2, 3])
    print(cs.x, cs.y, cs.L)
