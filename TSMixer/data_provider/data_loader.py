# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-09-08 15:33:03
# @email: 1499237580@qq.com
# @Software: Sublime Text
import pandas as pd
import numpy as np
import torch
import os
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import StandardScaler


class TSDataset(Dataset):
    def __init__(self, seq_size, feat_size, pred_size, root_path, file_name, target):
        self.seq_size = seq_size
        self.feat_size = feat_size
        self.pred_size = pred_size
        self.target = target
        self.data_path = os.path.join(root_path, file_name)
        self.__read_data()

    # def collate_fn(self, data, seq_size):
    def __read_data(self):
        data = (pd.read_csv(self.data_path, index_col=0)
                .fillna(method='ffill')
                .fillna(method='bfill')
                )
        print(data[self.target])
        self.date = data['date']
        data.drop('date', axis=1, inplace=True)
        target_data = (data[self.target]
                       .shift(periods=-self.pred_size)
                       .dropna()
                       .to_list()
                       )
        ts_y = []
        ts_x = []
        data = data.values.tolist()
        for i, j in enumerate(target_data):
            yi = target_data[i:i + self.pred_size]
            if len(yi) == 7:
                ts_y.append(yi)
                ts_x.append(data[i:i + self.pred_size])
        print(ts_y)
        print(ts_x)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        ts_x = self.data[idx, :]
        return ts_x


if __name__ == '__main__':
    seq_size = 7
    feat_size = 1
    pred_size = 7
    root_path = 'D:\\pythonproject\\TSMixer\\data'
    file_name = 'ts_test.csv'
    target = 'values'
    TSDataset = TSDataset(seq_size, feat_size, pred_size, root_path, file_name, target)
    data_loader = DataLoader(TSDataset, batch_size=4)
    for batch in data_loader:
        print(batch)
