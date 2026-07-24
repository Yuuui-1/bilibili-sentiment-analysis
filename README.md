# B站评论智能分析平台

基于 Flask + MongoDB + DeepSeek AI 的 Bilibili 评论采集、情感分析与可视化平台。

## 亮点

- **完整数据链路**：爬虫采集 → MongoDB 存储 → 情感分析 → 可视化 → AI 解读
- **真实 AI 分析**：DeepSeek API 对每张图表自动生成数据洞察，非模板文案
- **中文情感分析**：SnowNLP 分词 + 中文停用词过滤 + 情感打分（正面/中性/负面）
- **6 种可视化**：词云、性别饼图、等级折线图、点赞/回复柱状图、用户名词云
- **B站原生风格**：粉红渐变主题，导航切换流畅

## 功能

| 模块 | 说明 |
|------|------|
| 数据采集 | B站 API 评论爬虫，支持换视频链接重新采集 |
| 情感分析 | SnowNLP 中文情感打分，标注正面/中性/负面 |
| 数据看板 | 首页数据概览 + DeepSeek AI 洞察 + 评论样本 |
| 可视化图表 | 6 张 PyEcharts 图表，统一粉色主题布局 |
| AI 解读 | 每张图表页配 DeepSeek 实时数据分析 |

## 技术栈

| 层 | 技术 |
|----|------|
| 数据采集 | Python requests + B站 API |
| 数据库 | MongoDB + pymongo |
| 情感分析 | SnowNLP + jieba 分词 + 中文停用词 |
| 可视化 | PyEcharts（词云/饼图/柱状图/折线图） |
| AI 分析 | DeepSeek API（deepseek-chat） |
| Web | Flask + Jinja2 |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置
cp .env.example .env  # 填入 DEEPSEEK_API_KEY

# 3. 启动 MongoDB
mongod

# 4. 爬取数据（替换为目标视频链接）
python bilibili_pachong.py https://www.bilibili.com/video/BVxxxxxxxxx

# 5. 情感分析
python sentiment_analysis.py

# 6. 生成图表
python word_cloud.py && python user_comment.py && python user_sex.py && python user_level.py

# 7. 启动 Web
python app.py
```

打开 http://127.0.0.1:5000

## 项目结构

```
├── app.py                  # Flask Web + DeepSeek AI 集成
├── bilibili_pachong.py     # 评论爬虫（支持命令行传参）
├── sentiment_analysis.py   # SnowNLP 情感分析
├── user_comment.py         # 点赞排行柱状图
├── user_comment2.py        # 回复排行柱状图
├── user_level.py           # 等级分布折线图
├── user_sex.py             # 性别分布饼图
├── word_cloud.py           # 评论词云
├── word_cloud2.py          # 用户名云
├── config.py               # 配置中心
├── templates/              # HTML 模板 + 图表文件
├── static/                 # 静态资源
└── .env.example            # 环境变量模板
```
