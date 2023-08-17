# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-07-31 16:21:22
# @email: 1499237580@qq.com
# @Software: Sublime Text
from config import Config
import os
import logutil
import datetime
from data_provider.data_processe import Data_preprocess
from EXP_model import EXP_Model
import pandas as pd
from data_provider.data_request_test import Data_request
from data_provider.data_write import Data_writer

getlogger = logutil.getLogger()


class Args(Config):
    def __init__(self, city_code, city_name):
        super().__init__()
        self.city = city_name
        self.root_path = './data/'
        self.city_code = city_code
        self.data_path = os.path.join(self.city, self.city + ".csv")
        self.model_path = os.path.join("models", f"{self.city_code}_xgb.json")


def main():
    citys = {
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
    for city_code, city_name in citys.items():
        args = Args(city_code, city_name)
        data_path_name = os.path.join(args.root_path, args.city)
        if not os.path.exists(data_path_name):
            os.mkdir(data_path_name)
        if not os.path.exists(
                os.path.join("models", args.city)):
            os.mkdir(os.path.join("models", args.city))

        data_service = Data_request(args)
        data_service.data_request_load()

        preprocessor = Data_preprocess(args)
        preprocessor.preprocess_data()
        preprocessor.save_data(args.data_path)
        mymodel = EXP_Model(args)
        model_time = datetime.datetime.now().strftime("%Y-%m-%d")

        if not os.path.exists(f'./models/{city_code}_model_time.txt'):
            # 记录模型首次训练时间
            with open(f'./models/{city_code}_model_time.txt',
                      'w', encoding='utf-8') as f:
                f.write(model_time)
                mymodel.valid()
        else:
            # 存在训练记录后读取训练时间
            with open(f'./models/{city_code}_model_time.txt',
                      'r', encoding='utf-8') as f:
                model_time_old = f.read()
            timediff = pd.to_datetime(model_time_old) - pd.to_datetime(model_time)
            if timediff > pd.Timedelta(f"{args.train_period} days"):
                # 超过7天后重新训练
                with open(f'./models/{city_code}_model_time.txt',
                          'w', encoding='utf-8') as f:
                    f.write(model_time)
                    mymodel.valid()

        y_pred = mymodel.predict().reshape(-1, 1)
        y_pred = mymodel.std.inverse_transform(y_pred)
        df_pred = pd.DataFrame({'date': mymodel.date_x,
                                'value': y_pred.reshape(-1),
                                'city': city_name}
                               )
        df_pred.replace({np.nan: None}, inplace=True)
        df_pred.to_csv(os.path.join(data_path_name, city_name + '_pred.csv'))

        data_write = Data_writer(args, df_pred)
        data_write.data_write()


if __name__ == '__main__':
    main()
