"""
    随机生成无人机
    输入参数：二维平面边长，电池容量
"""
import random


class UAV(object):

    # 在length*length平面区域中随机生成一个位置
    def __init__(self, length, number):
        self.name = number
        self.x = float(format(random.uniform(0, length), '.2f'))  # v_i的横坐标，精确到两位小数
        self.y = float(format(random.uniform(0, length), '.2f'))  # v_i的纵坐标，精确到两位小数
        self.Q_i = 0  # v_i的总感知价值
        self.work_time = 0  # v_i的工作时间
        self.travel_time = 0  # v_i与充电站之间的飞行时间
        self.E_i = 0  # v_i的充电需求量
