# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-07-28 11:16:19
# @email: 1499237580@qq.com
# @Software: Sublime Text
import pandas as pd
import numpy as np
import os
import warnings
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logutil

getlogger = logutil.getLogger()

warnings.filterwarnings('ignore')


class EXP_Model:
    def __init__(self, args):
        self.city = args.city
        self.root_path = args.root_path
        self.data_path = args.data_path
        self.model_path = args.model_path
        self.is_weather = args.is_weather
        self.pred_len = args.pred_len
        if isinstance(args.years, list):
            self.years = args.years
        elif isinstance(args.years, str):
            self.years = args.years.split(',')
            self.years = [int(i) for i in self.years]
        self.years.sort(reverse=True)
        self.std = StandardScaler()
        self.df = pd.read_csv(os.path.join(self.root_path, self.data_path),
                              encoding="utf-8")
        self.date = self.df['date']
        getlogger.info('\n')
        getlogger.info("---------------")
        getlogger.info("%s模型计算开始" % self.city)
        getlogger.info("---------------")
        self.__time_decompose(self.df)
        self.model = xgb.XGBRegressor()

    def __time_decompose(self, df):
        # 缺失值填充
        df_true = (df
                   .fillna(method='ffill')
                   .fillna(method='bfill')
                   )
        # 拆分时间特征
        df_true['date'] = pd.to_datetime(df_true['date'])
        df_true['year'] = df_true['date'].dt.year
        df_true['month'] = df_true['date'].dt.month
        df_true['day'] = df_true['date'].dt.day
        df_true['hour'] = df_true['date'].dt.hour
        df_true['minute'] = df_true['date'].dt.minute
        df_true['dayofweek'] = df_true['date'].dt.dayofweek

        # 对目标列标准化

        self.std.fit(df_true[['value']].values)
        df_true['value'] = self.std.transform(df_true[['value']].values)

        self.df = df_true.drop('date', axis=1)
        getlogger.info("时间特征分解完成...")
        return

    def __sampling(self, df):
        sample_dict = {}
        max_year = np.max(self.years)
        sample_ratio = [1 - 0.1 * (max_year - i + 1) if max_year - i < 10 else 0.1 for i in self.years]

        for i, v in enumerate(self.years):
            sample_dict['d_%s' % v] = (df
                                       .query("year==%s" % int(v))
                                       .sample(frac=sample_ratio[i], random_state=666)
                                       )

        df_train = pd.concat([v for k, v in sample_dict.items()])
        x_train, x_valid, y_train, y_valid = train_test_split(
            df_train.drop('value', axis=1).values,
            df_train[['value']].values,
            random_state=666
        )
        getlogger.info("抽样与数据集划分完成...")
        return x_train, x_valid, y_train, y_valid

    def fit(self, x_train, y_train):
        self.model.fit(x_train, y_train)
        return

    def valid(self):
        x_train, x_valid, y_train, y_valid = self.__sampling(self.df)
        df_valid_x = (pd.DataFrame(x_valid,
                                   columns=['year', 'month',
                                            'day', 'hour',
                                            'minute', 'dayofweek']
                                   )
                      )
        df_valid_y = pd.DataFrame(y_valid, columns=['value'])
        df_valid = (pd
                    .concat([df_valid_x, df_valid_y], axis=1)
                    .query("(hour >= 11 & hour <= 15) | (hour >= 20 & hour <= 23)")
                    )
        df_valid_x = df_valid.drop('value', axis=1).values
        df_valid_y = df_valid[['value']].values

        self.fit(x_train, y_train)
        self.save_model(self.model_path)

        # 总体验证集准确率计算
        y_pred = self.predict(x_valid)
        yy = self.std.inverse_transform(y_pred.reshape(-1, 1)).astype(np.float32)
        yyy = self.std.inverse_transform(y_valid.reshape(-1, 1)).astype(np.float32)
        getlogger.info("验证集准确率: %s" % (1 - np.sum(np.abs(
            yyy - yy)) / np.sum(yyy)))

        # 高峰期验证集准确率计算
        y_valid_p = self.predict(df_valid_x)
        yy = self.std.inverse_transform(y_valid_p.reshape(-1, 1)).astype(np.float32)
        yyy = self.std.inverse_transform(df_valid_y.reshape(-1, 1)).astype(np.float32)
        getlogger.info("高峰期准确率: %s" % (1 - np.sum(np.abs(
            yyy - yy)) / np.sum(yyy)))

        getlogger.info('MAE: %s' % mean_absolute_error(y_pred=y_pred, y_true=y_valid))
        getlogger.info('MSE: %s' % mean_squared_error(y_pred=y_pred, y_true=y_valid))
        return

    def save_model(self, model_path):
        self.model.save_model(model_path)
        getlogger.info("模型保存完成...")
        return

    def predict(self, x=None):
        """
        预测函数，x默认为None，是None则自动预测未来
        """
        xgb_model = xgb.XGBRegressor()
        xgb_model.load_model(self.model_path)
        if x is None:
            x, self.date_x = self.generate_future_x()
        y_pred = xgb_model.predict(x)
        y_pred.astype(np.float32)
        return y_pred

    def generate_future_x(self):
        # 生成未来的时间特征
        date = pd.to_datetime(self.date)
        date_x = pd.date_range(start=np.max(date),
                               periods=self.pred_len * 96,
                               freq="15min")
        x_future = pd.DataFrame()
        x_future['date'] = date_x
        x_future['year'] = date_x.year
        x_future['month'] = date_x.month
        x_future['day'] = date_x.day
        x_future['hour'] = date_x.hour
        x_future['minute'] = date_x.minute
        x_future['dayofweek'] = date_x.dayofweek
        if self.is_weather:
            df_weather = pd.read_csv(os.path.join(self.root_path, 'data/CSV/市区县天气数据预测0718.csv'), encoding='utf-8')
            df_weather = df_weather[['data']]
            df_weather['date'] = (df_weather['data']
                                  .map(lambda x: eval(x)['forecasttime'])
                                  )
            cols = ['hum', 'maxtem', 'mintem', 'sitename', 'weathername']
            for i in cols:
                df_weather[i] = (df_weather['data']
                                 .map(lambda x: eval(x)[i])
                                 )
            df_weather['tem'] = (df_weather['maxtem'] +
                                 df_weather['mintem']) / 2
        return x_future.drop('date', axis=1).values.astype(np.float32), date_x
