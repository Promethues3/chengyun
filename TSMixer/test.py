# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-09-07 10:20:47
# @email: 1499237580@qq.com
# @Software: Sublime Text
import numpy as np
import pandas as pd

date = pd.date_range(start='2023-09-07', periods=30, freq='30 min')
values = list(range(30))
df = pd.DataFrame({'date': date, 'values': values})
df['values2'] = df['values'].shift(periods=-2)
l1 = df['values2'].dropna().to_list()
print([i for i in l1])
