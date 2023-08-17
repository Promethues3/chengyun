import requests
import numpy as np
import pandas as pd
from datetime import datetime
import json
import re
import logutil
import os
from config import Config

getlogger = logutil.getLogger()

# 初始化参数


class Args(Config):
    def __init__(self, city_code, city_name):
        super().__init__()
        self.city = city_name
        self.root_path = './data/' + self.city
        self.city_code = city_code
        #self.data_path = os.path.join(city_name, city_name + ".csv")
        self.data_path = [os.path.join(self.city, f"{self.city}_ele_load{i}.csv") for i in self.years]
        self.model_path = os.path.join("models",
                                       self.city, self.city + "_xgb.json"
                                       )


# 定义数据请求类
class Data_request:

    def __init__(self, args):
        self.root_path = './data/' + args.city
        if isinstance(args.years, list):
            self.years = args.years
            self.years.sort()
        elif isinstance(args.years, str):
            self.years = args.years.split(',')
            self.years = [int(i) for i in self.years]
        self.city = args.city
        self.city_code = args.city_code
        self.is_weather = args.is_weather
        self.data_path = [self.city + str(i) + '.csv' for i in self.years]
        self.df = None

    # 电力负荷实测数据接口调用
    def data_request_load(self):
        getlogger.info(self.root_path + '/' + self.city + '_ele_load' + '2023.csv')
        #print(self.root_path + '/' + self.city + '_ele_load' + '2023.csv')
        url = 'http://173.10.0.32:8090/DataService_nrkjzx/dataservice/getCloudData'
        current_year = datetime.now().year
        meas_type = '21032001'
        # 全量数据文件存在
        if os.path.isfile(self.root_path + '/' + self.city + '_ele_load' + '2023.csv'):

            # 判断全量文件最近时间
            latest_txt_path = self.root_path + '/' + self.city + 'latest_year.txt'
            with open(latest_txt_path, 'r') as file:
                latest_date = file.read()
                latest_date = re.sub("\n|\t", '', latest_date)
            df_origin = pd.read_csv(self.root_path + '/' + self.city + '_ele_load' + latest_date + '.csv')
            df_temp = df_origin

            # json csv文件解析
            df_cols = ['create_time', 'v00', 'v15', 'v30', 'v45']
            for col in df_cols:
                df_temp[col] = df_temp['data'].map(lambda x: eval(x)[col])
            df_temp = (df_temp
                       .rename({'create_time': 'date'}, axis=1)
                       .drop(['data', 'message', 'status',
                              'data_size'], axis=1)
                       )

            date = pd.to_datetime(df_temp['date']).max()

            temp_dict = {
                "code": "CYKJ_JHC_DLFHYC_SSFH",
                "tb_time": current_year,
                "pageNum": "-1",
                "condition": "AND id = %s AND meas_type = %s AND create_time > '%s'" % (self.city_code, meas_type, date)
            }
            json_info = json.dumps(temp_dict)
            data = bytes(json_info, "utf8")
            header = {"Content-Type": "application/json"}
            res = requests.post(url = url, data = data, headers = header, verify = False)
            data_json = res.json()
            df_incre = pd.DataFrame(data_json)

            # 合并全量文件和增量文件
            df_origin = pd.read_csv(self.root_path + '/' + self.city + '_ele_load' + str(current_year) + '.csv')
            df_save = pd.concat([df_incre, df_origin[['message', 'status', 'data_size', 'data']]])
            df_save.to_csv(self.root_path + '/' + self.city + '_ele_load' + str(current_year) + '.csv', encoding = 'utf-8', index = False)
            getlogger.info("%s%s年%s类型负荷增量数据合并成功" % (self.city, current_year, meas_type))

            for col in df_cols:
                df_save[col] = df_save['data'].map(lambda x: eval(x)[col])
            df_save = (df_save
                       .rename({'create_time': 'date'}, axis=1)
                       .drop(['data', 'message', 'status',
                              'data_size'], axis=1)
                       )
            latest_date = df_save['date'].max()
            latest_year = latest_date[:4]
            # 迭代全量文件最近时间
            txt_path = self.root_path + '/' + self.city + 'latest_year.txt'

            with open(txt_path, 'w') as file:
                file.write(str(latest_year))

        else:
            #         city_code = '001330900'
            #         meas_type = '21032001'
            #         date = '2023-07-18 00:00:00'

            for i in self.years:
                temp_dict = {
                    "code": "CYKJ_JHC_DLFHYC_SSFH",
                    "tb_time": i,
                    "pageNum": "-1",
                    "condition": "AND id = %s AND meas_type = %s" % (self.city_code, meas_type)
                }
                json_info = json.dumps(temp_dict)
                data = bytes(json_info, "utf8")
                header = {"Content-Type": "application/json"}
                res = requests.post(url = url, data = data, headers = header, verify = False)

                data_json = res.json()
                df = pd.DataFrame(data_json)

                df.to_csv(self.root_path + '/' + self.city + '_ele_load' + str(i) + '.csv', encoding = 'utf-8', index = False)

                getlogger.info("%s%s年%s类型负荷全量数据获取成功" % (self.city, i, meas_type))

                latest_year = self.years[-1]
                txt_path = self.root_path + '/' + self.city + 'latest_year.txt'

                with open(txt_path, 'w') as file:
                    file.write(str(latest_year))
        return


if __name__ == "__main__":
    # 定义参数
    #city = '0101330100'
    city_dict = {
        "0101330000": "浙江省",
        "0101330100": "杭州市",
        "0101330200": "宁波市",
        "0101330300": "温州市",
        "0101330400": "嘉兴市",
        "0101330500": "湖州市",
        "0101330600": "绍兴市",
        "0101330700": "金华市",
        "0101330800": "衢州市",
        "0101330900": "舟山市",
        "0101331000": "台州市",
        "0101331100": "丽水市"
    }
    for k, v in city_dict.items():
        city_code = k
        city_name = v
        args = Args(city_code, city_name)
        data_request = Data_request(args)
        data_request.data_request_load()
