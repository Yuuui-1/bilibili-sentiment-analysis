from flask import Flask, render_template
from pymongo import MongoClient
from config import MONGODB_URL
import os

app = Flask(__name__)


def get_db():
    client = MongoClient(MONGODB_URL)
    return client['bilibili']['new'], client


def analyze(col):
    """返回数据分析和 AI 洞察"""
    total = col.count_documents({})
    pos = col.count_documents({"sentiment_label": "正面"})
    neu = col.count_documents({"sentiment_label": "中性"})
    neg = col.count_documents({"sentiment_label": "负面"})
    male = col.count_documents({"user_sex": "男"})
    female = col.count_documents({"user_sex": "女"})

    # 平均情感得分
    pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$sentiment_score"}}}]
    r = list(col.aggregate(pipeline))
    avg_score = round(r[0]['avg'] * 100, 1) if r else 50

    # 正面评论平均点赞 vs 负面
    pipeline = [
        {"$match": {"like_count": {"$exists": True}}},
        {"$group": {"_id": "$sentiment_label", "avg": {"$avg": "$like_count"}}}
    ]
    like_by_sentiment = {d['_id']: round(d['avg'], 1) for d in col.aggregate(pipeline)}

    # 活跃用户
    pipeline = [{"$group": {"_id": "$user_name", "cnt": {"$sum": 1}}}, {"$sort": {"cnt": -1}}, {"$limit": 3}]
    top_users = [{"name": u['_id'], "count": u['cnt']} for u in col.aggregate(pipeline)]

    # 最高赞正面评论
    top_pos = col.find_one({"sentiment_label": "正面", "like_count": {"$exists": True}},
                           {"comment": 1, "user_name": 1, "like_count": 1, "sentiment_score": 1},
                           sort=[("like_count", -1)])

    # AI 洞察文本
    pos_pct = round(pos / total * 100, 1) if total else 0
    pos_likes = like_by_sentiment.get('正面', 0)
    neg_likes = like_by_sentiment.get('负面', 0)
    users_str = '、'.join(u['name'] for u in top_users)

    if pos_pct > 65:
        summary = f"整体评论偏正面（{pos_pct}%），社区氛围良好。正面评论平均 {pos_likes} 赞，高于负面评论的 {neg_likes} 赞，说明观众更倾向通过点赞表达认可。"
    elif pos_pct > 45:
        summary = f"评论情感分布均衡（正面 {pos_pct}%）。活跃用户 {users_str} 参与度最高。正面评论互动（{pos_likes} 赞/条）高于负面（{neg_likes} 赞/条）。"
    else:
        summary = f"负面评论占比较高（{neg} 条），存在讨论分歧。活跃用户包括 {users_str}，建议关注他们的具体反馈内容。"

    return {
        "total": total, "pos": pos, "neu": neu, "neg": neg,
        "male": male, "female": female, "avg_score": avg_score,
        "pos_pct": pos_pct, "pos_likes": pos_likes, "neg_likes": neg_likes,
        "top_users": top_users, "top_pos": top_pos, "summary": summary,
    }


@app.route('/')
def index():
    col, client = get_db()
    data = analyze(col)

    # 评论样本
    pos_samples = list(col.find({"sentiment_label": "正面"}, {"comment": 1, "user_name": 1, "sentiment_score": 1})
                       .sort("sentiment_score", -1).limit(4))
    neg_samples = list(col.find({"sentiment_label": "负面"}, {"comment": 1, "user_name": 1, "sentiment_score": 1})
                       .sort("sentiment_score", 1).limit(4))
    client.close()
    return render_template("zhuye.html", **data, pos_samples=pos_samples, neg_samples=neg_samples,
                           active_page="home")


@app.route('/<page>')
def chart_page(page):
    """统一的图表页面——嵌入原始图表 + 数据分析"""
    titles = {
        "top_comments_chart": "点赞排行 Top 10",
        "top_comments_chart2": "回复排行 Top 10",
        "gender_pie_chart": "用户性别分布",
        "user_level_line_chart": "用户等级分布",
        "wordcloud": "评论词云",
        "wordcloudid": "用户名词云",
    }
    if page not in titles:
        return "Not found", 404

    title = titles[page]
    filename = page + ".html"

    # 读取图表 HTML
    chart_path = os.path.join(app.template_folder, filename)
    chart_html = ""
    if os.path.exists(chart_path):
        with open(chart_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        # 保留 head 中的 script（加载 echarts.js）和 body 内容
        head_scripts = ""
        if '<head>' in raw and '</head>' in raw:
            head = raw.split('<head>')[1].split('</head>')[0]
            import re
            head_scripts = '\n'.join(re.findall(r'<script[^>]*>.*?</script>', head, re.DOTALL))
        body = raw
        if '<body>' in body:
            body = body.split('<body>')[1]
        if '</body>' in body:
            body = body.split('</body>')[0]
        chart_html = head_scripts + '\n' + body

    # 数据分析
    col, client = get_db()
    data = analyze(col)
    client.close()

    # 图表专属 AI 洞察
    page_insights = generate_page_insight(col, page, data)

    return render_template("chart_page.html", title=title, chart_html=chart_html,
                           data=data, insight=page_insights, active_page=page)


def generate_page_insight(col, page, data):
    """为每个图表页生成专属分析文字"""
    if page == "wordcloud":
        return f"从 {data['total']} 条评论中提取的高频关键词。正面评论占 {data['pos_pct']}%，热词反映了观众对内容的关注焦点。"
    if page == "wordcloudid":
        return f"用户名中出现频率最高的词汇。活跃用户如 {data['top_users'][0]['name']} 等，构成了社区的核心互动群体。"
    if page == "gender_pie_chart":
        return f"参与评论的用户中男性 {data['male']} 人、女性 {data['female']} 人。性别分布反映了该视频内容的受众结构。"
    if page == "user_level_line_chart":
        return f"用户的B站等级分布。高等级用户通常意味着更活跃的社区参与度和更高的内容消费深度。"
    if page == "top_comments_chart":
        return f"点赞最高的 {10} 条评论。这些评论代表了观众最认同的观点，整体情感偏正面（{data['pos_pct']}%）。正面评论平均 {data['pos_likes']} 赞，高于负面评论的 {data['neg_likes']} 赞。"
    if page == "top_comments_chart2":
        return f"回复数最高的 {10} 条评论。高回复数意味着引发了较多的讨论和互动，这些评论往往是话题的引爆点。"
    return ""


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
