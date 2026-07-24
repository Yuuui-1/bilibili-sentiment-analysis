# B站舆情分析系统

基于 Flask + MongoDB + PyEcharts 的 Bilibili 评论数据采集与可视化分析平台。

## 功能

- **数据采集**：通过 B站 API 自动爬取指定视频的评论数据（用户信息、评论内容、点赞数、回复数等）
- **数据存储**：MongoDB 存储评论和用户数据
- **可视化分析**：
  - 词云图（评论关键词）
  - 性别分布饼图
  - 用户等级分布折线图
  - 热门评论 Top 10
  - 点赞/回复排行
- **Web 展示**：Flask + HTML 模板渲染可视化页面

## 技术栈

| 层 | 技术 |
|----|------|
| 数据采集 | Python requests + B站 API |
| 数据库 | MongoDB + pymongo |
| 文本处理 | jieba 分词 + wordcloud |
| 可视化 | PyEcharts |
| Web 框架 | Flask |

## 项目结构

```
├── app.py                  # Flask Web 入口
├── bilibili_pachong.py     # B站评论爬虫（解析 API、分页抓取）
├── user_comment.py         # 评论数据处理
├── user_comment2.py        # 评论数据处理（扩展）
├── user_level.py           # 用户等级分析
├── user_sex.py             # 用户性别分析
├── word_cloud.py           # 词云生成
├── word_cloud2.py          # 词云生成（扩展）
├── templates/              # HTML 模板
│   ├── zhuye.html          # 首页
│   ├── wordcloud.html      # 词云页
│   ├── gender_pie_chart.html # 性别饼图
│   ├── level.html          # 等级分布
│   ├── top_comments_chart.html # 热评排行
│   └── ...
└── static/                 # 静态资源（CSS、JS、图片）
```

## 快速开始

```bash
# 安装依赖
pip install flask pymongo requests jieba wordcloud pyecharts

# 启动 MongoDB（需要本地 MongoDB 服务）
mongod

# 运行爬虫（修改 bilibili_pachong.py 中的视频 URL）
python bilibili_pachong.py

# 启动 Web 服务
python app.py
```

打开 http://127.0.0.1:5000
