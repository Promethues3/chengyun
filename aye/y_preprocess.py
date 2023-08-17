# -*- coding: utf-8 -*-
# @Author: libin
# @Date:   2023-08-09 19:39:35
# @E-mail: 1499237580@qq.com
# @Software: Sublime Text
import pandas as pd
import numpy as np
import os
import re
import warnings

warnings.filterwarnings('ignore')


class Data_preprocess:
    def __init__(self):
        self.root_path = 'data'
        self.data_path = [f'x{i+1}' for i in range(11)]
        self.df = pd.DataFrame()
        self.region = ['北京市', '天津市', '河北省', '山西省',
                       '内蒙古自治区', '辽宁省', '吉林省', '黑龙江省',
                       '上海市', '江苏省', '浙江省', '安徽省',
                       '福建省', '江西省', '山东省', '河南省',
                       '湖北省', '湖南省', '广东省', '广西壮族自治区',
                       '海南省', '重庆市', '四川省', '贵州省',
                       '云南省', '西藏自治区', '陕西省', '甘肃省',
                       '青海省', '宁夏回族自治区', '新疆维吾尔自治区']
        self.year = list(range(2007, 2022))
        self.region1 = self.region * len(self.year)
        self.region1.sort()
        self.df['region'] = self.region1
        self.df['year'] = self.year * len(self.region)
        self.df['id'] = self.df['region'] + self.df['year'].astype('str')

    def __region_union(self, df):
        df['region'] = df['region'].str.extract("(^..)")
        for i in self.region:
            df.loc[df['region'] == re.findall('^..', i)[0], 'region'] = i
        return df

    def x1_processing(self):
        data_path0 = os.path.join(self.root_path, self.data_path[0], 'gy.csv')
        data_path1 = os.path.join(self.root_path, self.data_path[0], 'jy.csv')
        df0 = (pd.read_csv(data_path0, encoding='gb18030')
               .sort_values(by='region')
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               )
        df0['region'] = self.region
        df0 = (df0.melt(id_vars='region')
               .rename({"variable": "year", "value": "gy"}, axis=1)
               .sort_values(by=['region', 'year'])
               )
        df0['year'] = df0['year'].str.replace("年", "").astype('int')
        df0 = df0.query("year>=2007 and year<=2021")

        df1 = (pd.read_csv(data_path1)
               .sort_values(by='region')
               .replace({"--": np.nan})
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               )
        df1['region'] = self.region
        df1 = (df1.melt(id_vars='region')
               .rename({"variable": "year", "value": "jy"}, axis=1)
               .sort_values(by=['region', 'year'])
               )
        df1['year'] = df1['year'].str.replace("年", "").astype('int')
        df1 = df1.query("year>=2007 and year<=2021")
        self.df['x1'] = ((df0['gy'].astype('float').values * 100000000) /
                         (df1['jy'].astype('float').values * 10000))

        return

    def x2_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[1], 'x2.csv')
        df1 = (pd.read_csv(data_path, encoding='gb18030')
               .query("year>=2007 and year<=2021")
               )
        df1['制造业增加值'] = df1['制造业增加值亿元'] * 100000000

        df1['gdp'] = df1['gdp'] * 100000000

        df1_1 = (df1.drop('制造业增加值亿元', axis=1)
                 .pivot(index='year', columns='region', values='制造业增加值')
                 )
        df1_2 = df1_1.shift(1, fill_value=0)
        df1_0 = df1_1.values - df1_2.values

        df2_1 = (df1.drop('制造业增加值亿元', axis=1)
                 .pivot(index='year', columns='region', values='gdp')
                 )
        df2_2 = df2_1.shift(1, fill_value=0)
        df2_0 = df2_1.values - df2_2.values
        df2 = df1_0 / df2_0
        df2 = (pd.DataFrame(df2, columns=df1_1.columns, index=df1_1.index)
               .reset_index()
               .melt(id_vars='year')
               .query("year != 2006")
               )
        df2['id'] = df2['region'] + df2['year'].astype('str')
        df2.drop(['year', 'region'], axis=1, inplace=True)

        self.df = (self.df
                   .merge(df2, how='left', on='id')
                   .rename({'value': 'x2'}, axis=1)
                   )

        return

    def x3_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[2], 'x3.csv')
        df = (pd.read_csv(data_path))
        df = df.melt(id_vars='region', var_name='year', value_name='x3')
        df['year'] = df['year'].str.replace('年', '').astype(int)
        df = (df
              .query("year>=2007 and year<=2021")
              .sort_values(by=['region', 'year'])
              )
        df['id'] = df['region'] + df['year'].astype('str')
        self.df = (self.df
                   .merge(df.drop(['year', 'region'], axis=1),
                          how='left', on='id')
                   .rename({'value': 'x3'})
                   )

        return

    def x4_processing(self):
        data_path0 = os.path.join(self.root_path, self.data_path[3])
        data_paths = [i for i in os.listdir(data_path0) if re.findall('^[0-9]{4}_2.csv', i)]
        df0 = pd.DataFrame()
        for data_path in data_paths:
            df = pd.read_csv(os.path.join(data_path0, data_path))
            df['region'] = df['region'].str.replace(' ', '')

            df['year'] = re.findall("^[0-9]{4}", data_path)[0]
            df[['有科技活动企业数', '企业数']] = (df[['有科技活动企业数', '企业数']]
                                       .fillna(method='ffill')
                                       .fillna(method='bfill')
                                       )

            df0 = pd.concat([df0, df])
        df0 = df0.sort_values(by=['region', 'year'])
        df0['region'] = self.df['region'].to_list()

        df0['id'] = df0['region'].str.cat(df0['year'].astype('str'))
        df0['x4'] = df0['有科技活动企业数'] / df0['企业数']
        self.df = (self.df
                   .merge(df0.drop(['region', 'year',
                                    '有科技活动企业数',
                                    '企业数'],
                                   axis=1),
                          how='left', on='id')
                   )

    def x5_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[4])
        data_paths = [i for i in os.listdir(data_path) if re.findall('^[0-9]{4}', i)]
        df1 = pd.DataFrame()
        for filename in data_paths:
            df0 = pd.read_csv(os.path.join(data_path, filename))
            df0['year'] = re.findall('^[0-9]{4}', filename)[0]
            df0.sort_values(by='region', inplace=True)
            df1 = pd.concat([df1, df0])
        df1['region'] = df1['region'].str.replace(" ", '')
        df1 = self.__region_union(df1)
        df1['id'] = df1['region'] + df1['year'].astype(str)
        df1 = (df1
               .drop(['region', 'year'], axis=1)
               )
        df2 = (pd
               .read_csv(os.path.join(data_path, '工业增加值.csv'))
               .melt(id_vars='region', value_name='工业增加值', var_name='year')
               )
        df2['year'] = (df2['year']
                       .str.extract("(^[0-9]{4})")
                       .astype('int')
                       )
        df2 = df2.query("year>=2007 and year<=2021")
        df2['id'] = df2['region'] + df2['year'].astype(str)
        df = pd.merge(df1, df2, how='right')

        df["主营业务收入"] = (df
                        .groupby('region')["主营业务收入"]
                        .fillna(method='ffill')
                        )
        df["主营业务收入"] = (df
                        .groupby('region')["主营业务收入"]
                        .fillna(method='bfill')
                        )
        df['x5'] = df["主营业务收入"].astype('float') / df["工业增加值"]
        df.drop(['region', 'year', '主营业务收入', '工业增加值'],
                axis=1,
                inplace=True
                )

        self.df = self.df.merge(df, how='left', on='id')
        return

    def x6_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[5])
        df1 = (pd
               .read_csv(os.path.join(data_path, 'x6.csv'))
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               .melt(id_vars='region', value_name='x6', var_name='year')
               )
        df1['year'] = (df1['year']
                       .str.extract("(^[0-9]{4})")
                       .astype('int')
                       )
        df1 = df1.query("year>=2007 and year<=2021")
        df1['id'] = df1['region'] + df1['year'].astype(str)
        df1.drop(['region', 'year'], axis=1, inplace=True)
        self.df = self.df.merge(df1, how='left', on='id')
        return

    def x7_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[6])
        df1 = (pd
               .read_csv(os.path.join(data_path, 'x7_1.csv'))
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               .melt(id_vars='region', value_name='x7_1', var_name='year')
               )
        df1['year'] = (df1['year']
                       .str.extract("(^[0-9]{4})")
                       .astype('int')
                       )
        df1 = df1.query("year>=2007 and year<=2021")
        df1 = self.__region_union(df1)
        df1['id'] = df1['region'] + df1['year'].astype(str)
        df1.drop(['region', 'year'], axis=1, inplace=True)

        df2 = (pd
               .read_csv(os.path.join(data_path, 'jy.csv'))
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               .melt(id_vars='region', value_name='x7_2', var_name='year')
               )
        df2['year'] = (df2['year']
                       .str.extract("(^[0-9]{4})")
                       .astype('int')
                       )
        df2 = df2.query("year>=2007 and year<=2021")
        df2 = self.__region_union(df2)
        df2['id'] = df2['region'] + df2['year'].astype(str)
        df2.drop(['region', 'year'], axis=1, inplace=True)

        df = pd.merge(df1, df2, how='outer', on='id')
        df['x7'] = df['x7_1'] / df['x7_2']
        df.drop(['x7_1', 'x7_2'], axis=1, inplace=True)

        self.df = self.df.merge(df, how='left', on='id')
        return

    def x8_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[7])
        df1 = (pd
               .read_csv(os.path.join(data_path, 'x8_1.csv'))
               .replace({'--': np.nan})
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               .melt(id_vars='region', value_name='x8_1', var_name='year')
               )
        df1['year'] = (df1['year']
                       .str.extract("(^[0-9]{4})")
                       .astype('int')
                       )
        df1 = df1.query("year>=2007 and year<=2021")
        df1 = self.__region_union(df1)
        df1['id'] = df1['region'] + df1['year'].astype(str)
        df1.drop(['region', 'year'], axis=1, inplace=True)

        df2 = (pd
               .read_csv(os.path.join(data_path, '规模以上工业企业利润总额(亿元).csv'))
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               .melt(id_vars='region', value_name='x8_2', var_name='year')
               )
        df2['year'] = (df2['year']
                       .str.extract("(^[0-9]{4})")
                       .astype('int')
                       )
        df2 = df2.query("year>=2007 and year<=2021")
        df2 = self.__region_union(df2)
        df2['id'] = df2['region'] + df2['year'].astype(str)
        df2.drop(['region', 'year'], axis=1, inplace=True)

        df = pd.merge(df1, df2, how='outer', on='id')
        df['x8'] = df['x8_1'].astype(float) / df['x8_2']
        df.drop(['x8_1', 'x8_2'], axis=1, inplace=True)
        self.df = self.df.merge(df, how='left', on='id')
        return

    def x9_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[8])
        df1 = (pd
               .read_csv(os.path.join(data_path, 'x9_1.csv'))
               .replace({'--': np.nan})
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               .melt(id_vars='region', value_name='x9_1', var_name='year')
               )
        df1['year'] = (df1['year']
                       .str.extract("(^[0-9]{4})")
                       .astype('int')
                       )
        df1 = df1.query("year>=2007 and year<=2021")
        df1 = self.__region_union(df1)
        df1['id'] = df1['region'] + df1['year'].astype(str)
        df1.drop(['region', 'year'], axis=1, inplace=True)

        df2 = (pd
               .read_csv(os.path.join(data_path, '工业增加值.csv'))
               .replace({'--': np.nan})
               .fillna(method='ffill', axis=1)
               .fillna(method='bfill', axis=1)
               .melt(id_vars='region', value_name='x9_2', var_name='year')
               )
        df2['year'] = (df2['year']
                       .str.extract("(^[0-9]{4})")
                       .astype('int')
                       )
        df2 = df2.query("year>=2007 and year<=2021")
        df2 = self.__region_union(df2)
        df2['id'] = df2['region'] + df2['year'].astype(str)
        df2.drop(['region', 'year'], axis=1, inplace=True)
        df = pd.merge(df1, df2, how='outer', on='id')
        df['x9'] = df['x9_1'].astype(float) / df['x9_2']
        df.drop(['x9_1', 'x9_2'], axis=1, inplace=True)
        self.df = self.df.merge(df, how='left', on='id')
        return

    def x10_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[9])
        data_paths = [i for i in os.listdir(data_path) if re.findall('^[0-9]{4}', i)]
        df1 = pd.DataFrame()
        for filename in data_paths:
            df0 = pd.read_csv(os.path.join(data_path, filename))
            df0['year'] = re.findall('^[0-9]{4}', filename)[0]
            df0.sort_values(by='region', inplace=True)
            df0['region'] = df0['region'].str.replace(' ', '')
            df0 = self.__region_union(df0)
            df1 = pd.concat([df1, df0])
        df1[['x10_2', 'x10_1']] = (df1
                                   .groupby('region')[['x10_2', 'x10_1']]
                                   .fillna(method='ffill')
                                   .values
                                   )
        df1[['x10_2', 'x10_1']] = (df1
                                   .groupby('region')[['x10_2', 'x10_1']]
                                   .fillna(method='bfill')
                                   .values
                                   )
        df1['x10'] = df1['x10_1'] / df1['x10_2']
        df1['id'] = df1['region'] + df1['year'].astype(str)
        df1.drop(['region', 'year', 'x10_1', 'x10_2'], axis=1, inplace=True)
        self.df = self.df.merge(df1, how='left', on='id')
        return

    def x11_processing(self):
        data_path = os.path.join(self.root_path, self.data_path[10], 'x11.csv')
        df = (pd
              .read_csv(data_path)
              .replace({'--': np.nan})
              .fillna(method='ffill', axis=1)
              .fillna(method='bfill', axis=1)
              .melt(id_vars='region', value_name='x11', var_name='year')
              )
        df['year'] = df['year'].str.extract("(^[0-9]{4})").astype('int')
        df = df.query("year>=2007 and year<=2021")
        df = self.__region_union(df)
        df['id'] = df['region'] + df['year'].astype(str)
        df.drop(['region', 'year'], axis=1, inplace=True)
        self.df = self.df.merge(df, how='left', on='id')
        return


if __name__ == '__main__':
    data_pre = Data_preprocess()
    data_pre.x4_processing()
