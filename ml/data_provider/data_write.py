# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-08-11 15:47:58
# @email: 1499237580@qq.com
# @Software: Sublime Text
import json
import pandas as pd
import requests


class Data_writer:
    def __init__(self, args, df):
        self.df = df
        self.df['date'] = pd.to_datetime(df['date'])
        self.url = None
        self.token = args.token
        self.id = args.city_code
        self.meas_type = args.meas_type
        self.datasource_id = args.city_code
        self.maker_name = args.maker_name
        self.__data_processe()

    def __data_processe(self):
        self.df['creat_date'] = self.df['date'].dt.date
        self.df['time'] = 'v' + (self.df['date']
                                 .dt.time.astype('str')
                                 .str.replace(':', '')
                                 .str.extract('(^.{4})')
                                 )
        self.df = (self.df
                   .pivot(index='creat_date',
                          columns='time',
                          values='value')
                   .reset_index()
                   )
        backward_col = self.df.iloc[:, 2:].columns.to_list()
        backward_col.append('v2400')
        self.df['v2400'] = self.df['v0000'].shift(-1)
        self.df.drop('v0000', axis=1, inplace=True)
        self.df['id'] = self.id
        self.df['meas_type'] = self.meas_type
        self.df['datasource_id'] = self.datasource_id
        self.df['maker_name'] = self.maker_name
        self.df = self.df[['id', 'meas_type',
                           'datasource_id', 'maker_name',
                           'creat_date'] + backward_col
                          ]
        data = self.df.to_dict('records')
        self.upload_data = {'token': self.token, 'data': data}
        return

    def __len__(self):
        return len(self.upload_data['data'])

    def __call__(self):
        return "预测数据处理和写入函数"

    def data_write(self):
        pass
