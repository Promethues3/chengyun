# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-07-19 09:30:54
# @email: 1499237580@qq.com
# @Software: Sublime Text
import requests
import numpy as np
import os
import pandas as pd
import requests
import json

# url = 'http://173.10.0.32:8090/DataService_nrkjzx/dataservice/getCloudData'

# temp_dict = {
#     "code": "CYKJ_JHC_DLFHYC_SSFH",
#     "tb_time": "2023",
#     "pageNum": "-1",
#     "condition": "AND id = 0101330900 AND meas_type = 21032001"
#     }
# json_info = json.dumps(temp_dict)
# data = bytes(json_info,"utf8")

# print(data)

# header = {"Content-Type":"application/json"}
# res = requests.post(url = url, data = data, headers = header,verify = False)

# data_json = res.json()
# df = pd.DataFrame(data_json)

# print(df)
# df.to_csv('C:/Users/vds67/Desktop/城云/CSV/舟山市全社会负荷2023.csv',encoding = 'utf_8_sig')


class Data_preprocess:
    def __init__(self, args):
        self.root_path = args.root_path
        self.year = args.year.split(',')
        self.city = args.city
        self.is_weather = args.is_weather
        self.data_path = [self.city + i + '.csv' for i in self.year]
        self.df = None

    def data_request(self):
        pass

    @staticmethod
    def weather_encode(values):
        """
        { relation的键值对字典 }

        :param      values:  The values
        :type       values:  list
        """
        if isinstance(values, list):
            value2id = {}
            id2value = {}
            for i, v in enumerate(values):
                if v not in value2id:
                    value2id[v] = i
                    id2value[i] = v
            return id2value, value2id
        else:
            raise ValueError("Invalid value provided.")

    def read_data(self):
        city_e_datapath = self.root_path + '/' + self.city + '_weather'
        city_e_datapath_exists = os.path.exists(city_e_datapath)

        city_datapath = [i for i in self.data_path if self.city in i]

        # if not city_datapath or not city_e_datapath_exists:
        #     raise("没有检测到历史数据，请重新请求数据...")

        # 处理电力负荷数据
        df = pd.DataFrame()
        for i in self.data_path:
            df1 = pd.read_csv(self.root_path + '/' + i)
            df = pd.concat([df, df1])
        print("电力负荷数据加载完成...")

        df_cols = ['create_time', 'v00', 'v15', 'v30', 'v45']
        for col in df_cols:
            df[col] = df['data'].map(lambda x: eval(x)[col])

        df = (df
              .rename({'create_time': 'date'}, axis=1)
              .drop(['data', 'message', 'status',
                     'data_size'], axis=1)
              )
        if self.is_weather:
            # city_e_datapath_exists = True
            # 处理天气数据
            df_weather = pd.read_csv(city_e_datapath)
            print("天气数据加载完成...")
            df_weather_cols = ['observtime', 'hum', 'rainfall', 'tem', 'weathername']
            for col in df_weather_cols:
                df[col] = df['data'].map(lambda x: eval(x)[col])

            df_weather = (df_weather
                          .rename({'observtime': 'date'}, axis=1)
                          .drop(['data', 'message', 'status',
                                 'data_size'], axis=1)
                          )
            # 将天气的类型进行编码
            df.replace({np.nan: None}, inplace=True)
            values = df['weathername'].to_list()
            with open(self.rootpath + '/' + 'weathername.txt', 'r', encoding='utf-8') as f:
                weathername = f.read().split('\n')
                id2value, value2id = self.weather_encode(self, weathername)

            df['weathername'] = [None if i is None else int(value2id[i]) for i in values]

            # 合并两个数据集
            df = df.merge(df_weather, on='date', how='left')
            df = (df
                  .astype({'hum': float,
                           'rainfall': float,
                           'tem': float,
                           'value': float})
                  )
        colname = df.columns.drop(['v00', 'v15', 'v30', 'v45'])
        df = (df
              .melt(id_vars=colname)
              .astype({'date': 'datetime64[ns]'})
              )

        # 调整日期
        for i in [15, 30, 45]:
            df.loc[df['variable'] == 'v'
                   + str(i),
                   'date'] = (pd.offsets
                              .Minute(i) +
                              df.loc[df['variable'] == 'v' + str(i),
                                     'date']
                              )

        self.df = (df
                   .drop('variable', axis=1)
                   .sort_values(by=['date'])
                   .replace({np.nan: None})
                   )

    def __getitem__(self):
        return self.df

    def __len__(self):
        return self.df.shape

    def save_data(self, data_path):
        self.df.to_csv(self.root_path + '/' + data_path,
                       encoding='GB18030', index=False)
        print('数据已保存...')
