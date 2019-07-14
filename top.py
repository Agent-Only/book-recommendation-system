import pandas as pd


def get_top_book():
    # 读取Books1.csv文件内容
    books = pd.read_csv('./data/Books1.csv', encoding='latin-1')
    books.columns = ['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication',
                     'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L']
    # print(books.shape)

    # 读取Ratings1.csv文件内容
    ratings = pd.read_csv('./data/Ratings1.csv', encoding='latin-1')
    ratings.columns = ['userid', 'bookid', 'score']
    # print(ratings.shape)

    ratings_new = ratings[ratings['bookid'].isin(books['ISBN'])]
    # print(ratings.shape)
    # print(ratings_new.shape)

    ratings_explicit = ratings_new[ratings_new['score'] != 0]
    # print(ratings_explicit.shape)

    ratings_count = pd.DataFrame(
        ratings_explicit.groupby(['bookid'])['score'].sum())
    top200 = ratings_count.sort_values('score', ascending=False).head(200)
    top200PD = top200.merge(books, left_index=True, right_on='ISBN')
    # print(top200PD)

    arr = top200PD.values
    top_len = len(top200PD)

    top_list = []
    data = {}

    for i in range(top_len):
        info = {}
        top_dict = {"item_id": arr[i][1]}
        info["recom_score"] = arr[i][0]
        info["title"] = arr[i][2]
        info["author"] = arr[i][3]
        info["year"] = arr[i][4]
        info["publisher"] = arr[i][5]
        info["img_l"] = arr[i][8]
        top_dict["info"] = info
        top_list.append(top_dict)

    data["recom_num"] = len(top_list)
    data["recom_result"] = top_list
    # print(data)

    return data


if __name__ == "__main__":
    top = get_top_book()
    print(top)
