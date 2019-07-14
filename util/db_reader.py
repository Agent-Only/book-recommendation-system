def get_user_like(rating_list):
    """

    :param rating_list: [{rating1}, {rating2}, ...]
    :return: dict: key:user_id, value:[item1, item2, ...]
    """
    user_like_dict = {}

    for row in rating_list:

        # 过滤得分小于 6.0 的 book
        # 即认为得分大于 6.0 的 book 可以为相似度提供贡献
        [id, user_id, book_id, score] = row.values()
        if float(score) < 6.0:
            continue
        if user_id not in user_like_dict:
            user_like_dict[user_id] = []
        user_like_dict[user_id].append(book_id)

    return user_like_dict


def get_user_rate(rating_list):
    """

   :param rating_list: [{rating1}, {rating2}, ...]
   :return: dict: key:user_id, value:[item1, item2, ...]
   """

    user_rate = {}

    for row in rating_list:

        # 过滤得分小于 6.0 的 book
        # 即认为得分大于 6.0 的 book 可以为相似度提供贡献
        [id, user_id, book_id, score] = row.values()
        if float(score) < 6.0:
            continue
        if user_id not in user_rate:
            user_rate[user_id] = []
            # score 简单归一化为 0~1
        item_rate = (book_id, int(score) / 10)
        user_rate[user_id].append(item_rate)

    return user_rate


def get_user_info(user_list):
    """

    :param user_list: [{user1}, {user2}, ...]
    :return: dict: key: user_id, value: [location, age]
    """
    user_info_dict = {}

    for row in user_list:
        [id, password, location, age, avatar_url] = row.values()
        if id not in user_info_dict:
            user_info_dict[id] = [location, age]

    return user_info_dict


def get_item_info(item_list):
    """

    :param item_list:
    :return: dict, key: item_id, value:[title, author]
    """

    item_info_dict = {}
    for row in item_list:
        [id, title, author, year, publisher, img_s, img_m, img_l] = row.values()
        if id not in item_info_dict:
            item_info_dict[id] = [title, author]

    return item_info_dict


def get_item_full_info(item_list):
    """

    :param item_list:
    :return: dict, key: item_id, value:[title, author]
    """

    item_info_dict = {}
    for row in item_list:
        [id, title, author, year, publisher, img_s, img_m, img_l] = row.values()
        if id not in item_info_dict:
            item_info_dict[id] = [title, author,
                                  year, publisher, img_s, img_m, img_l]

    return item_info_dict
