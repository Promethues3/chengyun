# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-09-07 11:06:40
# @email: 1499237580@qq.com
# @Software: Sublime Text
import torch
from torch import nn
from layers import TempProject, MixingLayer


class TSMixer:
    def __init__(self, seq_size, hidden_size,
                 feat_size, dropout_prob,
                 pred_size, mixinglayer_num=1,
                 hiddenlayer_num=0):
        self.MixingLayer = [MixingLayer(seq_size,
                                        hidden_size,
                                        feat_size,
                                        dropout_prob)
                            ] * mixinglayer_num
        self.TempProject = TempProject(seq_size,
                                       hidden_size,
                                       pred_size,
                                       hiddenlayer_num
                                       )

    def forward(self, x):
        output = x
        for i in self.MixingLayer:
            output = i.forward(x)
        output = self.TempProject.forward(output)
        return output


if __name__ == "__main__":
    seq_size = 128
    feat_size = 64  # 替换成你的输入特征维度
    hidden_size = 128  # 替换成你的隐藏层特征维度
    output_size = 10  # 替换成你的输出特征维度
    dropout_prob = 0.5  # 替换成你想要的dropout概率
    pred_size = 64
    x = torch.randn(hidden_size, feat_size)
    print(x.shape)
    model = TSMixer(seq_size, hidden_size,
                    feat_size, dropout_prob,
                    pred_size)
    print(model.forward(x).shape)
