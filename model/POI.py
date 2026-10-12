"""
    随机生成兴趣点
    输入参数：二维平面边长
"""
import random


class POI(object):

    # 在length*length平面区域中随机生成一个位置
    def __init__(self, length):
        self.x = float(format(random.uniform(0, length), '.2f'))  # o_i的横坐标，精确到两位小数
        self.y = float(format(random.uniform(0, length), '.2f'))  # o_i的纵坐标，精确到两位小数
        self.w_j = float(format(random.random(), '.2f'))  # o_i的效用权重，精确到两位小数


if __name__ == '__main__':
    poi = POI(10)
    print(poi.x, poi.y, poi.w_j)
