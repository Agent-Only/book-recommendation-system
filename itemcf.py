# -*coding:utf8-*-
"""
item cf main Algo
"""
import util.reader as reader
import numpy as np
import pandas as pd
import operator
import sys
import math

"""
公式：
similar[i][j] = u(i) ∩ u(j) / sqrt(u(i) * u(j))
predict[u][j] = ∑( i ∊ n(u) ∩ similar(j, k) ) similar[i][j] * rate[u][i]
"""


def main_flow():
    """
    main flow of itemcf
    """
    user_like = reader.get_user_like("./data/ratings.csv")
    user_rate = reader.get_user_rate("./data/ratings.csv")
    item_info = reader.get_item_info("./data/BX-Books.csv")

    # 根据用户评分计算 item 的相似度
    sim_info = cal_item_sim(user_like)

    # 根据用户评分，和 item 的相似度, 得出推荐结果
    recom_result = cal_recom_result(sim_info, user_rate)

    # 输出 debug 信息
    # 输出 item 的相似列表
    fixed_item_id = "050552533X"
    debug_item_sim(item_info, sim_info, fixed_item_id)

    # 输出 user 的推荐结果
    user_id = '246671'
    debug_recom_result(recom_result, item_info, user_id)


def debug_item_sim(item_info, sim_info, fixed_item_id):
    """
    show item similar info
    输出给定物品的相似度信息
    Args:
        item_info: dict, key:item_id, value: [title, author]
        sim_info: dict, key:item_id,
            value: dict, value_key [(item_id_1, sim_score), (item_id_2, sim_score), ...]
    """

    if fixed_item_id not in item_info:
        print("invalid item_id")
        return

    [title_fix, author_fix] = item_info[fixed_item_id]

    author_sim_list = []
    title_sim_list = []
    sim_score_list = []
    tmp_dict = {}
    for pair in sim_info[fixed_item_id]:
        item_id_sim = pair[0]
        sim_score = pair[1]
        if item_id_sim not in item_info:
            continue
        [title_sim, author_sim] = item_info[item_id_sim]
        title_sim_list.append(title_sim)
        author_sim_list.append(author_sim)
        sim_score_list.append(sim_score)

    tmp_dict = {"title_sim": title_sim_list,
                "author_sim": author_sim_list, "sim_score": sim_score_list}
    # 字典转化为表格输出
    table = pd.DataFrame.from_dict(tmp_dict)
    print(table)


def debug_recom_result(recom_result, item_info, user_id):
    """
    debug recom result
    输出给定用户的推荐信息
    Args:
        recom_result: key: user_id value: dict, value_key: item_id, value_value: recom_score
        item_info: dict, item_id, value:[title, author]
    """

    if user_id not in recom_result:
        print("invalid user_id")
        return

    item_title_list = []
    item_author_list = []
    recom_score_list = []
    tmp_dict = {}
    for pair in recom_result[user_id]:
        item_id = pair[0]
        recom_score = pair[1]
        if item_id not in item_info:
            continue
        [item_title, item_author] = item_info[item_id]
        item_title_list.append(item_title)
        item_author_list.append(item_author)
        recom_score_list.append(recom_score)

    tmp_dict = {"item_title": item_title_list,
                "item_author": item_author_list, "recom_score": recom_score_list}
    # 字典转化为表格输出
    recom_table = pd.DataFrame.from_dict(tmp_dict)
    print(recom_table)


def base_contribute_score():
    """
    item cf base sim contribution score by user
    固定贡献
    """
    return 1


def update_contribute_score(user_total_rate_num):
    """
    item cf update sim contribution score by user
    点击数目越少，贡献度越高，数目越多贡献度越低
    """
    return 1/math.log10(1 + user_total_rate_num)


def cal_item_sim(user_like):
    """
    calculate the similarity of item
    计算 item 之间的相似度
    Args:
      user_like: dict, key:user_id, value: [item_id1, item_id2, ...]
    Return:
      dict, key:item_id, value: dict, value_key:[(item_id_1, sim_score), (item_id_2, sim_score), ...]
    """
    # 评价 item 的公共用户
    co_appear = {}
    # 评价 item 的所有用户
    item_user_like_count = {}

    for user, item_list in user_like.items():
        for i in range(0, len(item_list)):
            item_id_i = item_list[i]
            item_user_like_count.setdefault(item_id_i, 0)
            item_user_like_count[item_id_i] += 1
            for j in range(i + 1, len(item_list)):
                item_id_j = item_list[j]

                co_appear.setdefault(item_id_i, {})
                co_appear[item_id_i].setdefault(item_id_j, 0)
                # 存储 item_i 对 item_j 的贡献
                co_appear[item_id_i][item_id_j] += update_contribute_score(
                    len(item_list))

                co_appear.setdefault(item_id_j, {})
                co_appear[item_id_j].setdefault(item_id_i, 0)
                # 存储 item_j 对 item_i 的贡献
                co_appear[item_id_j][item_id_i] += update_contribute_score(
                    len(item_list))

    item_sim_score = {}
    item_sim_score_sorted = {}
    for item_id_i, relate_item in co_appear.items():
        for item_id_j, co_count in relate_item.items():
            sim_score = co_count / \
                math.sqrt(
                    item_user_like_count[item_id_i] * item_user_like_count[item_id_j])
            item_sim_score.setdefault(item_id_i, {})
            item_sim_score[item_id_i].setdefault(item_id_j, 0)
            # 存储 item_i 对 item_j 的相似度得分
            item_sim_score[item_id_i][item_id_j] = sim_score

    # 对得分由高到低进行排序
    for item_id in item_sim_score:
        item_sim_score_sorted[item_id] = sorted(
            item_sim_score[item_id].items(), key=operator.itemgetter(1), reverse=True)

    return item_sim_score_sorted


def cal_recom_result(sim_info, user_rate):
    """
    recommend by itemcf
    使用 item cf 计算对用户的推荐结果
    Args:
      sim_info: item sim dict
      user_rate: user rate dict
    Return:
      dict, key: user_id, value: [(item_id1, recom_scroe1), (item_id2, recom_score2), ...]
    """
    # 有效评分次数
    recent_rate_num = 5
    # 仅保存相似度最高的 topk 项
    topk = 10
    recom_info = {}
    recom_info_sorted = {}

    for user_id in user_rate:
        rate_list = user_rate[user_id]
        recom_info.setdefault(user_id, {})
        for item_rate in rate_list[:recent_rate_num]:
            item_id = item_rate[0]
            if item_id not in sim_info:
                continue
            # 用户 u 对物品 i 的打分 (0 ~ 1)
            rate_score = item_rate[1]
            for item_sim_pair in sim_info[item_id][:topk]:
                item_sim_id = item_sim_pair[0]
                item_sim_score = item_sim_pair[1]
                recom_info[user_id][item_sim_id] = item_sim_score * rate_score

    for user_id in recom_info:
        recom_info_sorted[user_id] = sorted(
            recom_info[user_id].items(), key=operator.itemgetter(1), reverse=True)

    return recom_info_sorted


if __name__ == "__main__":
    main_flow()
