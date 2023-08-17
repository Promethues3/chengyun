# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-07-11 11:27:12
# @email: 1499237580@qq.com
# @Software: Sublime Text
import numpy as np
import pandas as pd
from data_provider.data_request import Data_preprocess


class Args:
    def __init__(self, root_path, year, city):
        self.root_path = root_path
        self.year = year
        self.city = city
        self.is_weather = False


if __name__ == '__main__':
    root_path = './data/CSV/'
    year = '2020,2021,2022,2023'
    city = '浙江省全社会负荷'
    args = Args(root_path, year, city)
    data_preprocess = Data_preprocess(args)
    data_preprocess.read_data()
    data_preprocess.save_data('zj_power.csv')
