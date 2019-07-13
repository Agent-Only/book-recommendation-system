# -*coding:utf8-*-
import csv
import os


def get_user_like(rating_file):
    """
    get user like
    获取 user 喜爱的 item 列表
    Args:
      rating_file: input_file
    Return:
      dict: key:user_id, value:[item1, item2, ...]
    """
    if not os.path.exists(rating_file):
        return {}
    num = 0

    with open(rating_file, encoding="latin-1") as f:
        data = csv.reader(f)
        user_like = {}

        for row in data:
            # 过滤表头
            if num == 0:
                num += 1
                continue

            # 过滤小于 3 列的行
            if len(row) < 3:
                continue
            [user_id, book_id, score] = row

            # 过滤得分小于 6.0 的 book
            # 即认为得分大于 6.0 的 book 可以为相似度提供贡献
            if float(score) < 6.0:
                continue
            if user_id not in user_like:
                user_like[user_id] = []
            user_like[user_id].append(book_id)

    return user_like


def get_user_info(user_info_file):
    """  
    get user info
    获取 user 的基本信息
    Args:
        user_info_file: input_file
    Return:
        dict: key: user_id, value: [location, age]
    """
    if not os.path.exists(user_info_file):
        return {}

    num = 0
    with open(user_info_file, encoding="latin-1") as f:
        data = csv.reader(f)
        user_info = {}

        for row in data:
            # 过滤表头
            if num == 0:
                num += 1
                continue

            # 过滤小于 n 列的行
            if len(row) < 3:
                continue

            # fix-me 过滤大于 n 列的行
            if len(row) > 3:
                continue

            [user_id, location, age] = row
            if user_id not in user_info:
                user_info[user_id] = [location, age]

    return user_info


def get_user_rate(rating_file):
    """
    get user rate
    获取 user 对 item 的评分列表
    Args:
      rating_file: input_file
    Return:
      dict: key:user_id, value:[(item1, rate1), (item2, rate2),  ...]
    """
    if not os.path.exists(rating_file):
        return {}
    num = 0

    with open(rating_file, encoding="latin-1") as f:
        data = csv.reader(f)
        user_rate = {}
        for row in data:
            # 过滤表头
            if num == 0:
                num += 1
                continue

            # 过滤小于 3 列的行
            if len(row) < 3:
                continue
            [user_id, book_id, score] = row

            # 过滤得分小于 6.0 的 book
            # 即认为得分大于 6.0 的 book 可以为相似度提供贡献
            if float(score) < 6.0:
                continue
            if user_id not in user_rate:
                user_rate[user_id] = []
                # score 简单归一化为 0~1
                item_rate = (book_id, int(score) / 10)
            user_rate[user_id].append(item_rate)

    return user_rate


def get_item_info(item_file):
    """
    get item info[title, author]
    获取 item 粗略信息
    Args:
      item_file: input item_info file
    Return:
      a dict, key: item_id, value:[title, author]
    """
    if not os.path.exists(item_file):
        return {}
    num = 0
    with open(item_file, encoding="latin-1") as f:
        data = csv.reader(f)
        item_info = {}

        for row in data:
            # 过滤表头
            if num == 0:
                num += 1
                continue

            # 过滤小于 8 列的行
            if len(row) < 8:
                continue

            # fix-me: 过滤大于 8 列的行
            if len(row) > 8:
                continue

            [book_id, title, author, year, publisher, img_s, img_m, img_l] = row
            if book_id not in item_info:
                item_info[book_id] = [title, author]

    return item_info


def get_item_full_info(item_file):
    """
    get item info[title, author, year, publisher, img_s, img_m, img_l]
    获取 item 完整信息
    Args:
      item_file: input item_info file
    Return:
      a dict, key: item_id, value:[title, author]
    """
    if not os.path.exists(item_file):
        return {}
    num = 0
    with open(item_file, encoding="latin-1") as f:
        data = csv.reader(f)
        item_info = {}

        for row in data:
            # 过滤表头
            if num == 0:
                num += 1
                continue

            # 过滤小于 8 列的行
            if len(row) < 8:
                continue

            # fix-me: 过滤大于 8 列的行
            if len(row) > 8:
                continue

            [book_id, title, author, year, publisher, img_s, img_m, img_l] = row
            if book_id not in item_info:
                item_info[book_id] = [title, author,
                                      year, publisher, img_s, img_m, img_l]

    return item_info


if __name__ == "__main__":
    # user_rate = get_user_rate("../data/Ratings1.csv")
    # print(user_rate)
    user_info = get_user_info("../data/Users1.csv")
    print(user_info)
