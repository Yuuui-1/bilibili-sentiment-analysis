from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from config import MONGODB_URL
import os

app = Flask(__name__)


def get_collection():
    client = MongoClient(MONGODB_URL)
    return client['bilibili']['new'], client


def render_chart(chart_name, title):
    """Read generated chart HTML and wrap in consistent layout."""
    chart_path = os.path.join(app.template_folder, chart_name)
    try:
        with open(chart_path, 'r', encoding='utf-8') as f:
            chart_html = f.read()
        # Extract just the body content from pyecharts output
        if '<body>' in chart_html:
            chart_html = chart_html.split('<body>')[1].split('</body>')[0]
        return render_template("chart_layout.html", chart_html=chart_html, title=title)
    except FileNotFoundError:
        return render_template("chart_layout.html", chart_html="<p style='padding:40px;text-align:center;color:#999;'>请先运行分析脚本生成图表</p>", title=title)


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

    # Most negative topic (keyword from negative comments)
    client.close()

    return render_template("zhuye.html",
                           total=total, pos=pos, neu=neu, neg=neg,
                           male=male, female=female,
                           avg_sentiment=avg_sentiment, pos_ratio=pos_ratio,
                           top_positive=top_positive)


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
