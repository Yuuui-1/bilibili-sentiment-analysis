# B站舆情分析系统

基于 Flask + MongoDB + PyEcharts 的 Bilibili 评论数据采集与可视化分析平台。

## 功能

- **数据采集**：通过 B站 API 自动爬取指定视频评论（含用户信息、评论内容、点赞数、回复数）
- **数据存储**：MongoDB 存储原始评论数据
- **可视化分析**：
  - 词云图 — 评论关键词可视化
  - 性别分布饼图 — 用户性别比例
  - 用户等级分布 — 等级折线图
  - 热门评论 Top 10 — 点赞/回复排行柱状图
  - 用户名云图 — 用户命名特征

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 MongoDB 地址和 B站 Cookie

# 3. 启动 MongoDB
mongod

# 4. 运行爬虫采集数据
python bilibili_pachong.py

# 5. 生成可视化图表
python user_comment.py
python user_comment2.py
python user_level.py
python user_sex.py
python word_cloud.py
python word_cloud2.py

# 6. 启动 Web 服务
python app.py
```

打开 http://127.0.0.1:5000

## 技术栈

| 层 | 技术 |
|----|------|
| 数据采集 | Python requests + B站 API |
| 数据库 | MongoDB + pymongo |
| 分词 | jieba |
| 可视化 | PyEcharts |
| Web | Flask |

## 项目结构

```
├── app.py                  # Flask Web 服务（14 个路由）
├── bilibili_pachong.py     # 评论爬虫（B站 API + MongoDB 入库）
├── config.py               # 配置（MongoDB URL、模板路径）
├── user_comment.py         # 热门评论 Top N（按点赞排序）
├── user_comment2.py        # 热门评论 Top N（按回复排序）
├── user_level.py           # 用户等级分布图
├── user_sex.py             # 用户性别饼图
├── word_cloud.py           # 评论词云生成
├── word_cloud2.py          # 用户名词云生成
├── templates/              # HTML 模板（14 个页面）
├── static/                 # 静态资源
├── .env.example            # 环境变量模板
└── requirements.txt        # Python 依赖
```
