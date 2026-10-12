import numpy as np


class KM:
    def __init__(self):
        self.matrix = None
        self.max_weight = 0.0
        self.row, self.col = 0, 0  # 源数据行列
        self.size = 0  # 方阵大小
        self.lx = None  # 左侧权值
        self.ly = None  # 右侧权值
        self.match = None  # 匹配结果
        self.slack = None  # 边权和顶标最小的差值
        self.visx = None  # 左侧是否加入增广路
        self.visy = None  # 右侧是否加入增广路

    # 调整数据
    def pad_matrix(self, min):
        if min:
            max = self.matrix.max() + 1.0
            self.matrix = max - self.matrix

        if self.row > self.col:  # 行大于列，添加列
            self.matrix = np.c_[self.matrix, np.array([[0.0] * (self.row - self.col)] * self.row)]
        elif self.col > self.row:  # 列大于行，添加行
            self.matrix = np.r_[self.matrix, np.array([[0.0] * self.col] * (self.col - self.row))]

    def reset_slack(self):
        self.slack.fill(self.max_weight + 1.0)

    def reset_vis(self):
        self.visx.fill(False)
        self.visy.fill(False)

    def find_path(self, x):
        self.visx[x] = True
        for y in range(self.size):
            # 如果是已经匹配过的点则跳过
            if self.visy[y]:
                continue
            tmp_delta = self.lx[x] + self.ly[y] - self.matrix[x][y]
            if tmp_delta == 0:
                # 添加到交替路径中
                self.visy[y] = True
                # 如果已经配对了，就让配对的这个人再找别家
                if self.match[y] == -1 or self.find_path(self.match[y]):
                    self.match[y] = x
                    return True
            # 不在交错路径中
            elif self.slack[y] > tmp_delta:
                self.slack[y] = tmp_delta
        return False

    def km_cal(self):
        for x in range(self.size):
            self.reset_slack()
            while True:
                self.reset_vis()
                if self.find_path(x):
                    break
                else:  # update slack
                    delta = self.slack[~self.visy].min()
                    self.lx[self.visx] -= delta
                    self.ly[self.visy] += delta
                    self.slack[~self.visy] -= delta

    def compute(self, datas, min=False):
        """
        :param datas: 权值矩阵
        :param min: 是否取最小组合，默认最大组合
        :return: 输出行对应的结果位置
        """
        self.matrix = np.array(datas) if not isinstance(datas, np.ndarray) else datas
        self.max_weight = self.matrix.sum()
        self.row, self.col = self.matrix.shape  # 源数据行列
        self.size = max(self.row, self.col)
        self.pad_matrix(min)
        # print(self.matrix)
        self.lx = self.matrix.max(1)
        self.ly = np.array([0.0] * self.size, dtype=float)
        self.match = np.array([-1] * self.size, dtype=int)
        self.slack = np.array([0.0] * self.size, dtype=float)
        self.visx = np.array([False] * self.size, dtype=bool)
        self.visy = np.array([False] * self.size, dtype=bool)

        self.km_cal()

        match = [i[0] for i in sorted(enumerate(self.match), key=lambda x: x[1])]
        result = []
        for i in range(self.row):
            result.append((i, match[i] if match[i] < self.col else -1))  # 没有对应的值给-1
        return result


if __name__ == '__main__':
    a = np.array([[0.0, 0.0], [0.0, 116.07], [0.0, 29.74]])
    km = KM()
    max_ = km.compute(a.copy())
    print("最大组合:", max_, a[[i[0] for i in max_], [i[1] for i in max_]])
