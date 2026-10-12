"""
    生成充电器模型
"""


class Charger(object):

    def __init__(self, number):
        self.name = number
        self.charge_power = 0  # 充电功率
        self.charge_pricie = 0  # 充电单价,与充电功率成正比，单位：元/时隙

