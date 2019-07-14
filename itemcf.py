# -*coding:utf8-*-
"""
item cf main Algo
"""
import math
import operator

"""
公式：
similar[i][j] = u(i) ∩ u(j) / sqrt(u(i) * u(j))
predict[u][j] = ∑( i ∊ n(u) ∩ similar(j, k) ) similar[i][j] * rate[u][i]
"""


def get_user_recom_result(user_id, user_like, user_rate, item_full_info):
    sim_info = cal_item_sim(user_like)

    recom_result = cal_recom_result(sim_info, user_rate)

    recom_list = recom_result[user_id]
    recom_dict = {}
    recom_info_list = []
    for pair in recom_list:
        item_id = pair[0]
        recom_score = pair[1]
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

    return recom_dict


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
    return 1 / math.log10(1 + user_total_rate_num)


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
            sim_score = co_count / math.sqrt(
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
    # 仅保存相似度最高的 top k 项
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
