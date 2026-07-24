from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from config import MONGODB_URL
import os

app = Flask(__name__)


def get_collection():
    client = MongoClient(MONGODB_URL)
    return client['bilibili']['new'], client


def render_chart(chart_name, title):
    """Read generated chart HTML and inject a back-to-home link."""
    chart_path = os.path.join(app.template_folder, chart_name)
    try:
        with open(chart_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        return "<p style='padding:40px;text-align:center'>请先运行分析脚本生成图表</p>", 404
    # Inject a floating back button
    back_btn = """
    <div style="position:fixed;top:14px;left:14px;z-index:9999;">
        <a href="/" style="
            display:inline-block;background:#FB7299;color:#fff;padding:8px 18px;
            border-radius:20px;text-decoration:none;font-size:14px;font-family:'Microsoft YaHei',sans-serif;
            box-shadow:0 2px 8px rgba(251,114,153,.3);
        ">← 返回首页</a>
    </div>"""
    html = html.replace('</body>', back_btn + '</body>')
    return html


@app.route('/')
def index():
    col, client = get_collection()
    total = col.count_documents({})

    # Sentiment stats
    pos = col.count_documents({"sentiment_label": "正面"})
    neu = col.count_documents({"sentiment_label": "中性"})
    neg = col.count_documents({"sentiment_label": "负面"})

    # Gender stats
    male = col.count_documents({"user_sex": "男"})
    female = col.count_documents({"user_sex": "女"})

    # Sentiment-detail samples
    positive_samples = list(col.find(
        {"sentiment_label": "正面"},
        {"comment": 1, "user_name": 1, "sentiment_score": 1, "_id": 0}
    ).sort("sentiment_score", -1).limit(5))

    negative_samples = list(col.find(
        {"sentiment_label": "负面"},
        {"comment": 1, "user_name": 1, "sentiment_score": 1, "_id": 0}
    ).sort("sentiment_score", 1).limit(5))

    # Sentiment insights
    avg_sentiment = 0
    pipeline = [
        {"$group": {"_id": None, "avg_score": {"$avg": "$sentiment_score"}}}
    ]
    result = list(col.aggregate(pipeline))
    if result:
        avg_sentiment = round(result[0]['avg_score'] * 100, 1)

    pos_ratio = round(pos / total * 100, 1) if total > 0 else 0

    # Top liked positive comment
    top_positive = col.find_one(
        {"sentiment_label": "正面"}, {"comment": 1, "user_name": 1, "like_count": 1, "_id": 0},
        sort=[("like_count", -1)]
    )

    insights = get_chart_insights(col)
    client.close()

    return render_template("zhuye.html",
                           total=total, pos=pos, neu=neu, neg=neg,
                           male=male, female=female,
                           avg_sentiment=avg_sentiment, pos_ratio=pos_ratio,
                            top_positive=top_positive, insights=insights)


def get_chart_insights(col):
    """Generate AI-powered or rule-based insights from chart data."""
    total = col.count_documents({})
    pos = col.count_documents({"sentiment_label": "正面"})
    neg = col.count_documents({"sentiment_label": "负面"})

    pipeline = [
        {"$match": {"like_count": {"$exists": True}}},
        {"$group": {"_id": "$sentiment_label", "avg_likes": {"$avg": "$like_count"}}}
    ]
    like_stats = {d['_id']: d for d in col.aggregate(pipeline)}

    pipeline = [{"$group": {"_id": "$user_name", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 3}]
    top_users = list(col.aggregate(pipeline))

    insights = {
        "positive_pct": round(pos / total * 100, 1) if total else 0,
        "neg_pct": round(neg / total * 100, 1) if total else 0,
        "top_users": [{"name": u['_id'], "count": u['count']} for u in top_users[:3]],
        "pos_avg_likes": round(like_stats.get('正面', {}).get('avg_likes', 0), 1),
        "neg_avg_likes": round(like_stats.get('负面', {}).get('avg_likes', 0), 1),
    }

    if insights['positive_pct'] > 60:
        insights["summary"] = f"整体评论偏正面（{insights['positive_pct']}%），社区氛围良好。正面评论平均 {insights['pos_avg_likes']} 赞，高于负面评论，说明观众更倾向于通过点赞表达认同。"
    elif insights['neg_pct'] > 30:
        insights["summary"] = f"负面评论占比 {insights['neg_pct']}%，存在一定讨论分歧。活跃用户包括 {'、'.join(u['name'] for u in insights['top_users'])}，建议关注他们的反馈。"
    else:
        insights["summary"] = f"评论情感分布均衡。活跃用户 {'、'.join(u['name'] for u in insights['top_users'])} 参与度最高。正面评论互动（{insights['pos_avg_likes']} 赞/条）高于负面（{insights['neg_avg_likes']} 赞/条）。"
    return insights


@app.route('/api/stats')
def api_stats():
    col, client = get_collection()
    stats = {
        "total": col.count_documents({}),
        "positive": col.count_documents({"sentiment_label": "正面"}),
        "neutral": col.count_documents({"sentiment_label": "中性"}),
        "negative": col.count_documents({"sentiment_label": "负面"}),
    }
    client.close()
    return jsonify(stats)


@app.route('/gender_pie_chart')
def gender_pie_chart():
    return render_chart("gender_pie_chart.html", "性别分布")

@app.route('/top_comments_chart')
def top_comments_chart():
    return render_chart("top_comments_chart.html", "点赞排行 Top 10")

@app.route('/top_comments_chart2')
def top_comments_chart2():
    return render_chart("top_comments_chart2.html", "回复排行 Top 10")

@app.route('/user_level_line_chart')
def user_level_line_chart():
    return render_chart("user_level_line_chart.html", "用户等级分布")

@app.route('/wordcloud')
def wordcloud():
    return render_chart("wordcloud.html", "评论词云")

@app.route('/wordcloudid')
def wordcloudid():
    return render_chart("wordcloudid.html", "用户名词云")

@app.route('/level')
def level():
    return render_template("level.html")

@app.route('/comments_show')
def comments_show():
    return render_template("comments_show.html")


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
