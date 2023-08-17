# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-08-15 14:36:57
# @email: 1499237580@qq.com
# @Software: Sublime Text
from y_preprocess import Data_preprocess
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd
import os
from utils import calculate_weights
import numpy as np


is_standardscaler = True


def y_pca_main():
    # y的预处理
    if not os.path.exists('df_y.csv'):
        data_pre = Data_preprocess()
        data_pre.x1_processing()
        data_pre.x2_processing()
        data_pre.x3_processing()
        data_pre.x4_processing()
        data_pre.x5_processing()
        data_pre.x6_processing()
        data_pre.x7_processing()
        data_pre.x8_processing()
        data_pre.x9_processing()
        data_pre.x10_processing()
        data_pre.x11_processing()
        data_pre.df.to_csv("df_y.csv",
                           encoding='gbk',
                           index=False)
        df_y = data_pre
    else:
        df_y = pd.read_csv("df_y.csv", encoding='gbk')

    # 标准化
    y_values0 = (df_y
                 .drop(['year', 'region', 'id'], axis=1)
                 )
    col_name = y_values0.columns
    if is_standardscaler:
        std = StandardScaler()
        std.fit(y_values0.values)
        y_values = std.transform(y_values0.values)
    else:
        y_values = y_values0
    y_values0 = (pd
                 .DataFrame(y_values, columns=col_name)
                 .fillna(method='bfill')
                 .fillna(method='ffill')
                 )

    # 熵权法
    y_weights = calculate_weights(y_values0.values)
    y_weights = pd.DataFrame({"var": col_name.to_list(),
                              "y_weights": y_weights}
                             )
    y_weights.to_csv("y_weights.csv",
                     encoding="gbk",
                     index=False
                     )
    y_ = np.dot(y_values0.values,
                y_weights[['y_weights']].values
                )
    y_ = pd.Series(y_.reshape(-1))
    y_ = (pd
          .concat([df_y[['year', 'region', 'id']], y_], axis=1)
          .rename({0: 'y_'}, axis=1)
          )
    print(y_)


if __name__ == '__main__':
    y_pca_main()
