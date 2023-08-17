# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-08-15 18:51:15
# @email: 1499237580@qq.com
# @Software: Sublime Text
import numpy as np


def calculate_entropy(p_values):
    return -np.sum(p_values * np.log2(p_values))


def calculate_weights(data):
    num_attributes = len(data[0])
    num_samples = len(data)

    attribute_probabilities = []
    for i in range(num_attributes):
        attribute_column = [data[j][i] for j in range(num_samples)]
        unique_values, counts = np.unique(attribute_column, return_counts=True)
        probabilities = counts / num_samples
        entropy = calculate_entropy(probabilities)
        attribute_probabilities.append(entropy)

    total_entropy = np.sum(attribute_probabilities)
    weights = [entropy / total_entropy for entropy in attribute_probabilities]
    return weights


if __name__ == "__main__":

    # 示例数据
    data = np.array([[3, 2, 1],
                     [4, 3, 1],
                     [2, 3, 2],
                     [1, 1, 1]])

    weights = calculate_weights(data)
    print("计算得到的权重：", weights)
