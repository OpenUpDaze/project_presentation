# 循环几次数据，损失就很小了，记下循环损失为nan
import torch
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler  # 导入归一化模块
import time

feature_number = 1  # 设置特征数目
out_prediction = 1  # 设置输出数目
learning_rate = 0.00001  # 设置学习率0.00001
epochs = 10 # 设置训练次数
Myseed = 2022  # 设置随机种子分关键，不然每次划分的数据集都不一样，不利于结果复现

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号


'''导入数据'''

csv_path = 'housing.csv'
housing = pd.read_csv(csv_path)
x_pd, y_pd = housing.iloc[:, 7:8], housing.iloc[:, -2:-1]

'''对每列（特征）归一化'''


# # feature_range控制压缩数据范围，默认[0,1]
# scaler = MinMaxScaler(feature_range=[0, 1])  # 实例化，调整0,1的数值可以改变归一化范围
#
# X = scaler.fit_transform(x_pd)  # 将标签归一化到0,1之间
# Y = scaler.fit_transform(y_pd)  # 将特征归于化到0,1之间

'''对每列数据执行标准化'''

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()                                  # 实例化
X = scaler.fit_transform(x_pd)                        # 标准化特征
Y = scaler.fit_transform(y_pd)                           # 标准化标签

# x = scaler.inverse_transform(X) # 这行代码可以将数据恢复至标准化之前


'''划分数据集'''


X = torch.tensor(X, dtype=torch.float32)  # 将数据集转换成torch能识别的格式
Y = torch.tensor(Y, dtype=torch.float32)

torch_dataset = torch.utils.data.TensorDataset(X, Y)  # 组成torch专门的数据库

# 划分训练集测试集与验证集
torch.manual_seed(seed=Myseed)  # 设置随机种子分关键，不然每次划分的数据集都不一样，不利于结果复现
train, test = torch.utils.data.random_split(torch_dataset, [14448, 6192])  # 先将数据集拆分为训练集（共14448组），测试集（6192组） # hyd 总长度一定要与数据集中数字数据长度一致 14448+6192 = 20640

# 再将训练集划分批次，每batch_size个数据一批（测试集与验证集不划分批次）
train_data = torch.utils.data.DataLoader(train, batch_size=32, shuffle=True)

'''训练部分'''


class Model(torch.nn.Module):
    def __init__(self, n_feature, n_output):  # n_feature为特征数目，这个数字不能随便取,n_output为特征对应的输出数目，也不能随便取
        self.n_feature = n_feature
        self.n_output = n_output
        super(Model, self).__init__()
        self.input_layer = torch.nn.Linear(self.n_feature, 20)  # 输入层
        self.hidden1 = torch.nn.Linear(20, 16)  # 1类隐藏层
        self.hidden2 = torch.nn.Linear(16, 10)  # 2类隐藏
        self.predict = torch.nn.Linear(10, self.n_output)  # 输出层
        self.ReLU = torch.nn.ReLU()  # hyd 激活函数

    def forward(self, x):
        '''定义前向传递过程'''
        out = self.ReLU(self.input_layer(x))
        out = self.ReLU(self.hidden1(out))
        out = self.ReLU(self.hidden2(out))
        out = self.predict(out)  # 回归问题最后一层不需要激活函数
        # 除去feature_number与out_prediction不能随便取，隐藏层数与其他神经元数目均可以适当调整以得到最佳预测效果
        return out


model = Model(n_feature=feature_number, n_output=out_prediction)  # 这里直接确定了隐藏层数目以及神经元数目，实际操作中需要遍历

optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
criterion = torch.nn.MSELoss(reduction='mean')  # 误差计算公式，回归问题采用均方误差

loss_array = []
for epoch in range(epochs):  # 整个数据集迭代次数
    for batch_idx, (data, target) in enumerate(train_data):
        logits = model(data)  # 前向计算结果（预测结果）
        loss = criterion(logits, target)  # 计算损失
        optimizer.zero_grad()  # 梯度清零
        loss.backward()  # 后向传递过程
        optimizer.step()  # 优化权重与偏差矩阵
    print('epoch = ', epoch, 'loss = ', loss.item())
    loss_array.append(loss.item())


pre_array = []
test_array = []
model.eval()  # 启动测试模式
for test_x, test_ys in test:
    pre = model(test_x)
    print(pre.item())
    pre_array.append(pre.item())
    test_array.append(test_ys.item())


# 可视化
plt.figure()
plt.scatter(test_array, pre_array, color='blue', alpha=1/7)
#plt.plot([0, 52], [0, 52], color='black', linestyle='-')
# plt.xlim([-0.05, 52])
# plt.ylim([-0.05, 52])
plt.xlabel('true')
plt.ylabel('prediction')
plt.title('true vs prection')




print('run time =', time.process_time(), 's')

epoch_array = [i for i in range(epochs)]
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(epoch_array, loss_array, 'r', label='loss')
ax.set_xlabel('epoch')
ax.set_ylabel('loss')
fig.savefig('fig.png')
plt.show()




