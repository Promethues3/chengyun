# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-08-09 17:10:32
# @email: 1499237580@qq.com
# @Software: Sublime Text
import os
from config import Config


class Args(Config):
    def __init__(self, city_code, city_name):
        super().__init__()
        self.root_path = 'data'
        self.city = city_name
        self.city_code = city_code
        self.data_path = os.path.join(city, city + ".csv")
        self.model_path = os.path.join("models", self.city, self.city + "_xgb.json")


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
    for year in args.years:
        os.system(f"""mv ./data/{args.city}_ele_load{year}.csv ./data/{args.city}/""")
    os.system(f"""mv ./data/{args.city}latest.txt ./data/{args.city}/""")
