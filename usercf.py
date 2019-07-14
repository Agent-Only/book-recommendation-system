# -*coding:utf8-*-
"""
user cf main Algorithm
"""
import math
import operator


def get_user_recom_result(user_id, user_rate, item_full_info):
    item_rate_by_user = transfer_user_rate(user_rate)
    user_sim = cal_user_sim(item_rate_by_user)
    recom_result = cal_recom_result(user_rate, user_sim)

    recom_dict = {}
    recom_info_list = []
    for pair in recom_result[user_id]:
        [item_id, recom_score] = pair
        if item_id not in item_full_info:
            continue
        [title, author, year, publisher, img_s,
         img_m, img_l] = item_full_info[item_id]
        info_dict = {}
        tmp_dict = {"recom_score": recom_score, "title": title, "author": author, "year": year, "publisher": publisher,
                    "img_l": img_l}
        info_dict["item_id"] = item_id
        info_dict["info"] = tmp_dict
        recom_info_list.append(info_dict)

    recom_dict["recom_num"] = len(recom_info_list)
    recom_dict["recom_result"] = recom_info_list

    # print(recom_dict)

    return recom_dict


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
        for user_id_j, co_num in relate_user.items():
            user_sim_info[user_id_i].setdefault(user_id_j, 0)
            user_sim_info[user_id_i][user_id_j] = co_num / math.sqrt(user_rate_count[user_id_i]
                                                                     * user_rate_count[user_id_j])
    # 排序
    for user_id in user_sim_info:
        user_sim_info_sorted[user_id] = sorted(
            user_sim_info[user_id].items(), key=operator.itemgetter(1), reverse=True)

    return user_sim_info_sorted


def cal_recom_result(user_rate, user_sim_info):
    """  
    recom by user cf algorithm
    Args:
      user_rate: key: user_id, value: [(item_id1, rate_score1), (item_id2, rate_score2), ...]
      user_sim_info: dict, key: user_id_i, value: [(user_id_j, score_1), (user_id_k, score_2), ...]
    Return:
      dict, key: user_id, value: [(item_id1, recom_scroe1), (item_id2, recom_score2), ...]
    """
    recom_result = {}
    recom_result_sorted = {}
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
                item_sim_score = pair[1]
                recom_result[user_id][item_id_j] = item_sim_score

    for user_id in recom_result:
        recom_result_sorted[user_id] = sorted(
            recom_result[user_id].items(), key=operator.itemgetter(1), reverse=True)

    return recom_result_sorted


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
    return 1 / math.log10(1 + item_user_rate_count)
