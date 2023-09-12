# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-09-07 09:05:56
# @email: 1499237580@qq.com
# @Software: Sublime Text
import torch
from torch import nn


class TempProject:
    def __init__(self, batch_size, hidden_size, pred_size, layer_num):
        self.input_size = batch_size
        self.hidden_size = hidden_size
        self.output_size = pred_size
        if layer_num == 0:
            self.fc = nn.ModuleList()
            self.fc.append(nn.Linear(self.input_size, self.output_size))
        else:
            self.head_linear = nn.Linear(self.input_size,
                                         self.hidden_size)
            self.tail_linear = nn.Linear(self.hidden_size,
                                         self.output_size)
            self.fc = nn.ModuleList()
            self.fc.append(self.head_linear)
            for i in range(layer_num - 1):
                self.fc.append(nn.Linear(hidden_size, hidden_size))
            self.fc.append(self.tail_linear)

    def forward(self, x):
        x = x.T
        for fc in self.fc:
            x = fc(x)
        return x.T


class MixingLayer:
    def __init__(self, batch_size, hidden_size,
                 input_size, dropout_prob):
        self.TimeMixing = TimeMixing(
            batch_size,
            hidden_size,
            input_size,
            dropout_prob
        )
        self.FeatMixing = FeatMixing(
            batch_size,
            hidden_size,
            input_size,
            dropout_prob
        )

    def forward(self, x):
        output = self.TimeMixing.forward(x)
        output = self.FeatMixing.forward(output)
        return output


class FeatMixing:
    """
    This class describes a feat mixing.
    """

    def __init__(self, batch_size, hidden_size,
                 feat_size, dropout_prob):
        self.bn = nn.BatchNorm1d(feat_size)
        self.FeatMLP = FeatMLP(
            feat_size,
            hidden_size,
            feat_size,
            dropout_prob
        )

    def forward(self, x):
        output = self.bn(x)
        output = self.FeatMLP(output)
        return output + x


class TimeMixing:
    """
    This class describes a time mixing.
    """

    def __init__(self, batch_size, hidden_size,
                 feat_size, dropout_prob):
        self.bn = nn.BatchNorm1d(feat_size)
        self.TimeMLP = TimeMLP(
            batch_size,
            hidden_size,
            batch_size,
            dropout_prob
        )

    def forward(self, x):
        output = self.bn(x)
        output = output.T
        output = self.TimeMLP.forward(output)
        return output.T + x


class TimeMLP(nn.Module):
    """docstring for TimeMLP(nn.Module)"""

    def __init__(self, input_size, hidden_size,
                 output_size, dropout_prob):
        super(TimeMLP, self).__init__()
        self.fc = nn.Linear(input_size, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout_prob)

    def forward(self, x):
        x = self.fc(x)
        x = self.relu(x)
        x = self.dropout(x)
        return x


class FeatMLP(nn.Module):
    """docstring for TimeMLP(nn.Module)"""

    def __init__(self, input_size, hidden_size,
                 output_size, dropout_prob):
        super(FeatMLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout_prob)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.dropout2 = nn.Dropout(dropout_prob)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        x = self.dropout2(x)
        return x


if __name__ == "__main__":
    batch_size = 128
    input_size = 64  # 替换成你的输入特征维度
    hidden_size = 128  # 替换成你的隐藏层特征维度
    output_size = 10  # 替换成你的输出特征维度
    dropout_prob = 0.5  # 替换成你想要的dropout概率
    x = torch.randn(hidden_size, input_size)
    print(x.shape)
    model = TempProject(batch_size, hidden_size, output_size, 2)
    print(model.forward(x))
