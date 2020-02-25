# 简易图书推荐系统

### 截图

| 图书首页                                                     | 模糊搜索                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| ![Screen Shot 2019-07-15 at 1.27.19 AM](http://ww3.sinaimg.cn/large/006tNc79ly1g50c7pdxstj31bf0u0x1e.jpg) | ![Screen Shot 2019-07-15 at 1.28.33 AM](http://ww4.sinaimg.cn/large/006tNc79ly1g50c7rsln4j31bf0u0wrt.jpg) |
| 图书评分                                                     | 图书推荐                                                     |
| ![Screen Shot 2019-07-15 at 1.27.39 AM](http://ww3.sinaimg.cn/large/006tNc79ly1g50c7s9se7j31bf0u0wnf.jpg) | ![Screen Shot 2019-07-15 at 1.37.28 AM](http://ww2.sinaimg.cn/large/006tNc79ly1g50c7tabfxj31bf0u01kx.jpg) |
| 个人信息                                                     |                                                              |
| ![Screen Shot 2019-07-15 at 1.37.46 AM](http://ww3.sinaimg.cn/large/006tNc79ly1g50c7tjx7hj31bf0u00z8.jpg) |                                                              |



### 概述

一个简单的图书推荐系统，可在现有数据源上对用户进行简单的图书推荐。

支持用户添加和更新评分，并更新推荐结果。

### 实现

前端实现较简单， vuetify 本身是成熟的响应式框架，我只在样式和布局上修改一些组件的预设。

主要的工作在前后端跨域请求数据和前端的用户状态管理问题。

#### 项目组成

```
Vue + Vuetify + Flask + SQLAlchemy + mysql
```

#### 前端依赖

1. 组件样式: `vuetify`, `material-design-icons-iconfont`
2. 路由处理: `vue-router`
3. ajax 请求: `axios`
4. 时间处理: `moment`

#### 后端依赖

1. Web框架：`Flask`
2. 处理跨域请求：`flask_cors`
3. 数据库ORM框架：`Flask-SQLAlchemy`
4. 数据处理：`Pandas`, `Numpy`, `math`, `operator`

#### 开发工具

操作系统：`MacOS 10.14.15`

前端IDE：`Visual Studio Code`

后端IDE:  `Pycharm`

数据库：`Mysql 8.0.15`, `redis 5.0.5`



### 数据源

数据源下载地址：http://www2.informatik.uni-freiburg.de/~cziegler/BX/

使用的数据源来自开源的 2004 年的图书数据库，原始文件为 CSV 格式。

#### 数据库表结构

使用 MySQL 数据库，共三张表 Book，User，Rating，Book 表为图书基本信息，User 表为用户基本信息，Rating 表为用户对特定图书的评分。

##### ER 图：

| Navicat 生成                                                 | DBViewer生成                                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| ![Screen Shot 2019-07-15 at 10.26.22 AM](http://ww4.sinaimg.cn/large/006tNc79ly1g50c7o4z3qj30ms0pi77h.jpg) | ![Screen Shot 2019-07-15 at 10.26.05 AM](http://ww2.sinaimg.cn/large/006tNc79ly1g50c7sifqsj30l40d2myj.jpg) |

数据量较大，Book 表和 User 表的数据约 30万行，导入后预览如下：

| User 表                                                      | Book 表                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| ![Screen Shot 2019-07-15 at 1.44.06 AM](http://ww1.sinaimg.cn/large/006tNc79ly1g50c7p0rq1j31c00u04qp.jpg) | ![Screen Shot 2019-07-15 at 1.43.52 AM](http://ww4.sinaimg.cn/large/006tNc79ly1g50c7qj0w7j31c00u0hdt.jpg) |
| Rating 表                                                    |                                                              |
| ![Screen Shot 2019-07-15 at 1.43.59 AM](http://ww2.sinaimg.cn/large/006tNc79ly1g50c7u7p4cj31c00u018k.jpg) |                                                              |



### 功能实现

#### 数据预处理

使用 Python 的 Pandas 库，对 CSV 文件进行了行遍历，过滤了一些字段中编码非 utf-8 与数据列数目不正确的列，再使用 Navicat 的 Import Wizard 工具将 CSV 文件导入为 MySQL Table。

#### 用户登陆

前台向后台发送登陆表单的信息，同时接受后台发送的用户详细信息存储在浏览器本地缓存(localStorage), 以在前端显示用户头像，用户名等 Profile.

```javascript
login() {
      Vue.prototype.$http
        .post("/login", this.userInfo)
        .then(response => {
          if (response.data.status == "success") {
            // 存储登陆信息在客户端浏览器中
            let userFullInfo = response.data.data;
            localStorage.setItem("LOGIN_USER", JSON.stringify(userFullInfo));
            this.message = "登陆成功";
            Snackbar.success(this.message);
      			// 登陆成功后跳转页面
            this.$router.push({ name: "Index" });
          } else {
            this.message = "登陆失败，原因为" + response.data.errMsg;
            Snackbar.error(this.message);
          }
        })
        .catch(error => {
          console.log(error);
          Snackbar.error(error);
        });
    }
```

后台接受前台 post 的表单数据，与后台 User 表进行验证，并返回对应状态码给前台：

```python
@app.route('/login', methods=['POST'])
def login():
    response = {}
    user_id = request.form['userId']
    password = request.form['password']
    login_user = User.query.filter_by(id=user_id).first()
    if login_user is not None:
        if login_user.password == password:
            response['status'] = 'success'
            response['data'] = User.as_dict(login_user)
            return json.dumps(response)
        else:
            response['status'] = 'fail'
            response['errMsg'] = '密码不正确'
            return json.dumps(response)
    else:
        response['status'] = 'fail'
        response['errMsg'] = '用户名不存在'
        return json.dumps(response)
```



#### 添加评价

前端以表单形式添加一条评价记录，后端通过获取参数使用数据库方法查询是否已有评分记录，已有则更新评分，否则新建评分。

前端使用 post 方法发送表单数据：

```javascript
// 发送用户评分请求
addRate() {
      this.dialog = false;
      this.form.userId = this.userId;
      this.form.bookId = this.item.item_id;
      this.form.score = this.rating * 2; // 0～5分制 => 0~10分制
      console.log(this.form);
      Vue.prototype.$http
        .post("/rating/add", this.form)
        .then(response => {
          if (response.data.status == "success") {
            this.message = "评价成功";
           ...
          } else {
            ...
          }
        })
        .catch(error => {
          console.log(error);
        });
    },
```

后端响应：

```python
# 添加用户评分
@app.route('/rating/add', methods=['POST'])
def add_rate():
    user_id = request.form['userId']
    book_id = request.form['bookId']
    score = request.form['score']
    rating = Rating.query.filter_by(user_id=user_id, book_id=book_id).first()
    if rating is not None:
        rating.score = score
    else:
        db.session.add(Rating(user_id=user_id, book_id=book_id, score=score))
    db.session.commit()
    response = {'status': 'success'}
    return json.dumps(response)
```



#### 基于协同过滤推荐

```python
# 基于物品相似度的协同过滤推荐公式：
similar[i][j] = u(i) ∩ u(j) / sqrt(u(i) * u(j))
predict[u][j] = ∑( i ∊ n(u) ∩ similar(j, k) ) similar[i][j] * rate[u][i]
```
推荐算法为协同过滤。计算相似度然后根据相似度排序，对用户的行为进行遍历，形成推荐列表。

**相似度中贡献度的计算函数：**

```python
def update_contribute_score(user_total_rate_num):
    """
    item cf update sim contribution score by user
    点击数目越少，贡献度越高，数目越多贡献度越低
    """
    return 1 / math.log10(1 + user_total_rate_num)
```

**计算相似度（以基于物品推荐为例）：**

```python
# itemcf.py
def cal_item_sim(user_like):
    # 评价 item 的公共用户
    co_appear = {}
    # 评价 item 的所有用户
    item_user_like_count = {}
    for user, item_list in user_like.items():
        for i in range(0, len(item_list)):
            ....
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
    	...
    	#  排序实现
      return item_sim_score_sorted
```



#### 模糊搜索

使用数据库中间件封装完成的方法对数据库中的所有字段进行遍历，相似的行转化为为列表输出。

```python
# 根据字段查询书籍
@app.route('/book/search/<content>')
def search_book(content):
    rows = Book.query.filter(
        or_(Book.id.like("%" + content + "%") if content is not None else "",
            Book.title.like("%" + content + "%") if content is not None else "",
            Book.author.like("%" + content + "%") if content is not None else "",
            Book.publisher.like("%" + content + "%") if content is not None else "",
            Book.year.like("%" + content + "%") if content is not None else "")
    ).limit(100)

    response = {}
		...

    return json.dumps(response)
```



### 项目构建

#### 前端

##### 下载项目

```bash
git clone https://github.com/ShiroCheng/vue-admin-vuetify.git
git checkout Book-Recommend-Flask-backend
cd vue-admin-vuetify
```

##### 安装依赖

```shell
npm install
```

##### 以开发模式(热加载)启动

```shell
npm run serve
```

打开 [http://localhost:3000](http://localhost:3000/) 查看 demo

如果热加载失败 更改 `vue.config.js`

```javascript
module.exports = {
  chainWebpack: config => {
    config.resolve
      .symlinks(true)
  }
}
```

##### 以生产模式启动

```shell
npm run build
```

##### 提示和修复文件

```shell
npm run lint
```

#### 后端

##### 下载项目

```shell
git clone https://github.com/ShiroCheng/Book_Recommend_System.git
cd  Book_Recommend_System
```

##### 配置依赖

````shell
conda create -n book_system python=3.6
source activate book_system (Unix) / activate book_system (Windows)
pip install flask flask_cors flask-sqlalchemy pandas numpy sqlalchemy 
````

##### 运行 Flask

```bash
python app.py
```


