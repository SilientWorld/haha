import numpy as np
import random

userNumber = 10
BSNumber = 5


class BS:
    def __init__(self, CPU, BD, locationX, locationY, range, priceCPU, priceBD):
        self.CPU = CPU
        self.BD = BD
        self.location = [locationX, locationY]
        self.range = range
        self.priceCPU = priceCPU
        self.priceBD = priceBD


class User:
    def __init__(self, CPU, BD, locationX, locationY):
        self.CPU = CPU
        self.BD = BD
        self.location = [locationX, locationY]


class Algorithm1():
    ##------全局变量
    M = 3  # 背包个数
    N = 4  # 物体个数

    # 背包尺寸数组
    bin_size = np.zeros(M)
    # 物品尺寸
    item_size = np.zeros((N, M), dtype=int)
    # 收益函数
    profit = np.zeros((N, M), dtype=int)
    # 存储选择元素的
    S = []  # 使
    S_hat = []  # 列表

    def __init__(self, M, N, bin_size, item_size, profit):
        self.M = M
        self.N = N
        self.bin_size = bin_size
        self.item_size = item_size
        self.profit = profit
        self.S = [] * M  # 列表里存放集合
        self.S_hat = []

    def printArgs(self):
        # 输出检验初始化的数据
        print("M=%d,N=%d" % (self.M, self.N))
        print(self.bin_size.shape, self.bin_size)
        print(self.item_size.shape, self.item_size)
        print(self.profit.shape, self.profit)

    def lp_01knapsack(self, j):
        # 第j列，对应第j个背包的情况
        depth = j

        n, c = int(self.N), int(self.bin_size[depth])
        dp = [[0 for jindex in range(c + 1)] for index in range(n + 1)]
        for k in range(c + 1):
            dp[0][k] = 0

        # depth = j
        # 价值函数，需要提取profit矩阵的第j列  错了  是Pj
        value_j = [self.Pj[index][0] for index in range(self.N)]
        for i in range(1, n + 1):
            for k in range(1, c + 1):
                dp[i][k] = dp[i - 1][k]
                if k >= self.item_size[i - 1][depth] and dp[i][k] < dp[i - 1][k - self.item_size[i - 1][depth]] + \
                        value_j[i - 1]:
                    dp[i][k] = dp[i - 1][k - self.item_size[i - 1][depth]] + value_j[i - 1]
        # return dp
        # 或者，返回被选择的物品
        x = [False for i in range(n)]
        selected = []
        ctmp = int(self.bin_size[depth])
        for i in range(n, 0, -1):
            if dp[i][ctmp] > dp[i - 1][ctmp]:
                x[i - 1] = True
                ctmp -= self.item_size[i - 1][depth]
        for i in range(n):
            if x[i]:
                selected.append(i)
        return selected

    def next_bin_j(self, j):
        Sj_hat = self.lp_01knapsack(j)
        self.S_hat.append(Sj_hat)
        # 步骤2 分解Pj  收益函数是Pj
        P1j = np.zeros((self.N, len(self.Pj[0])), dtype=int)
        # 复制j列  但每次削减后，都是当前第0  列
        for i in range(self.N):
            P1j[i][0] = self.Pj[i][0]
            if i in Sj_hat:
                P1j[i][:] = self.Pj[i][0]

        P2j = self.Pj - P1j
        # 步骤3
        if j < self.M - 1:  # 控制下标
            # set P_j+1 = P2j
            # 移除包Cj所在的列，也就是删除j列
            self.Pj = np.delete(arr=P2j, obj=0, axis=1)
            # 运行Next-Bin(j+1)   Sj+1 = ...
            self.next_bin_j(j + 1)  # Sj+1

    def next_bin_j_helper(self):
        # 根据 self.Sj_hat构建Si
        for i in range(len(self.S_hat) - 1, -1, -1):
            if i == len(self.S_hat) - 1:
                # 最后一个元素 Si_hat = Si   Si是列表，里面是集合  Si hat是np.array格式，不能直接转换为集合
                self.S.append(set(self.S_hat[i]))
            else:  # 只用考虑后一个元素
                behind = self.S  # 把这个元素和当前的合并  当前的S就是前一个的结果
                set_cur = set(self.S_hat[i])
                # print(behind,type(behind))
                union1 = set()  # 计算Sj+1往后元素的并集
                for i, val in enumerate(behind):
                    # print("val:",val,"type(val):",type(val))
                    union1 = union1.union(val)
                    # print("union1:",union1)
                # 把 Sj hat 变为集合，然后与上面并集做差
                diff = set_cur.difference(union1)
                # Sj = Sj+1 + diff   S中已经有后面的所有背包的结果
                self.S.append(diff)

    def next_bin(self):
        S = []
        # Pj = self.profit

        self.Pj = np.copy(self.profit)
        # print(id(Pj),id(self.profit))   id 不同，所以是深拷贝
        self.next_bin_j(0)
        self.next_bin_j_helper()
        print(self.S)
        return self.S


def init_data():
    M, N = BSNumber, userNumber


    # s = np.array([[1,1,1],[2,3,3],[2,3,4],[1,2,3]],dtype=int)  # 物体在每个背包中尺寸N*M  N物品数量
    # c = np.array([2,3,4],dtype=int)  #背包容量
    # p =np.array([[3,1,5],[1,1,1],[5,15,25],[25,15,5]],dtype=int)
    # p = np.array([[3, 22, 5], [22, 1, 22], [22, 15, 25], [25, 15, 22]], dtype=int)
    return M, N, s, c, p


def main(M, N, c, s, p):
    algorithm = Algorithm1(M, N, c, s, p)
    # algorithm.printArgs()
    # 下面进入算法流程
    algorithm.next_bin()


if __name__ == '__main__':
    M, N, s, c, p = init_data()
    main(M, N, c, s, p)
