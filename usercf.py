# -*coding:utf8-*-
"""
user cf main Algo
"""
import util.reader as reader
import numpy as np
import pandas as pd
import operator
import sys
import math


def main_flow():
    """
    main flow of user cf
    """
    user_rate = reader.get_user_rate("./data/ratings.csv")

    item_rate_by_user = transfer_user_rate(user_rate)
    # 计算 user 相似度
    user_sim = cal_user_sim(item_rate_by_user)

    # 根据 user 评分, 和 user 的相似度, 得出推荐结果
    recom_result = cal_recom_result(user_rate, user_sim)

    user_id = "250405"
    # 测试用户相似度
    debug_user_sim(user_sim, user_id)
    # 测试用户推荐结果
    debug_recom_result(recom_result, user_id)


def debug_user_sim(user_sim, user_id):
    """
    show user_sim
    Args:
      user_sim: dict, key: user_id_i, value: [(user_id_j, score_1), (user_id_k, score_2), ...]
      user_id: str
    Return:
      Null
    """
    user_sim_list = user_sim[user_id]
    user_id_list = []
    sim_score_list = []
    tmp_dict = {}

    # 转换为表格
    for pair in user_sim_list:
        user_id_j = pair[0]
        sim_score = pair[1]
        user_id_list.append(user_id_j)
        sim_score_list.append(sim_score)
    tmp_dict = {"user_id": user_id_list, "sim_score": sim_score_list}
    table = pd.DataFrame.from_dict(tmp_dict)
    print(table)


def debug_recom_result(recom_result, user_id):
    """  
    show recom_result
    Args:
      recom_result: dict, key: user_id, value: dict, value_key: item_id, value_value: recom_score
      user_id: str
    Return:
      Null
    """
    recom_dict = recom_result[user_id]
    recom_item_list = []
    recom_score_list = []
    tmp_dict = {}

    # 转换为表格输出
    for recom_item, recom_score in recom_dict.items():
        recom_item_list.append(recom_item)
        recom_score_list.append(recom_score)
    tmp_dict = {"recom_item": recom_item_list, "recom_score": recom_score_list}
    table = pd.DataFrame.from_dict(tmp_dict)
    print(table)


def transfer_user_rate(user_rate):
    """
    get item by user_rate
    Args: 
      user_rate, key: user_id, value: [(item_id1, rate_score1), (item_id2, rate_score2), ...]
    Return:
      dict, key: item_id, value: [user_id1, user_id2]
    """
    item_rate_by_user = {}
    for user_id in user_rate:
        rate_list = user_rate[user_id]
        for pair in rate_list:
            item_id = pair[0]
            item_rate_by_user.setdefault(item_id, [])
            item_rate_by_user[item_id].append(user_id)
    return item_rate_by_user


def cal_user_sim(item_rate_by_user):
    """
    cal user sim info
    Args: 
      item_rate_by_user, key: item_id, value: [user_id1, user_id2]
    Return:
      dict, key: user_id_i, value: [(user_id_j, score_1), (user_id_k, score_2), ...]
    """
    co_appear = {}
    user_rate_count = {}
    for item_id, user_list in item_rate_by_user.items():
        for i in range(0, len(user_list)):
            user_id_i = user_list[i]
            user_rate_count.setdefault(user_id_i, 0)
            user_rate_count[user_id_i] += update_contribute_score(
                len(user_list))
            for j in range(i + 1, len(user_list)):
                user_id_j = user_list[j]
                co_appear.setdefault(user_id_i, {})
                co_appear[user_id_i].setdefault(user_id_j, 0)
                co_appear[user_id_i][user_id_j] += update_contribute_score(
                    len(user_list))
                co_appear.setdefault(user_id_j, {})
                co_appear[user_id_j].setdefault(user_id_i, 0)
                co_appear[user_id_j][user_id_i] += update_contribute_score(
                    len(user_list))

    user_sim_info = {}
    user_sim_info_sorted = {}
    for user_id_i, relate_user in co_appear.items():
        user_sim_info.setdefault(user_id_i, {})
        for user_id_j, conum in relate_user.items():
            user_sim_info[user_id_i].setdefault(user_id_j, 0)
            user_sim_info[user_id_i][user_id_j] = conum / \
                math.sqrt(user_rate_count[user_id_i]
                          * user_rate_count[user_id_j])
    # 排序
    for user_id in user_sim_info:
        user_sim_info_sorted[user_id] = sorted(
            user_sim_info[user_id].items(), key=operator.itemgetter(1), reverse=True)

    return user_sim_info_sorted


def cal_recom_result(user_rate, user_sim_info):
    """  
    recom by user cf algo
    Args:
      user_rate: key: user_id, value: [(item_id1, rate_score1), (item_id2, rate_score2), ...]
      user_sim_info: dict, key: user_id_i, value: [(user_id_j, score_1), (user_id_k, score_2), ...]
    Return:
      dict, key: user_id, value: dict, value_key: item_id, value_value: recom_score
    """
    recom_result = {}
    topk_user = 10
    item_num = 5
    for user_id, item_list in user_rate.items():
        tmp_dict = {}
        for item_id in item_list:
            tmp_dict.setdefault(item_id, 1)
        recom_result.setdefault(user_id, {})
        if user_id not in user_sim_info:
            continue
        for pair in user_sim_info[user_id][:topk_user]:
            user_id_j = pair[0]
            sim_score = pair[1]
            if user_id_j not in user_rate:
                continue
            for pair in user_rate[user_id_j][:item_num]:
                item_id_j = pair[0]
                recom_result[user_id].setdefault(item_id_j, sim_score)

    return recom_result


def base_contribute_score():
    """
    user cf base sim contribution score by user
    固定贡献
    """
    return 1


def update_contribute_score(item_user_rate_count):
    """  
    user cf contribution score update
    惩罚被更多 user 评分过的 item，评分数越多贡献越小
    Args:
        item_user_rate_count: how many user have rated this item
    Return:
        contribution score
    """
    return 1/math.log10(1 + item_user_rate_count)


if __name__ == "__main__":
    main_flow()
