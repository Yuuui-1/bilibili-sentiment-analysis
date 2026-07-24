from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from config import MONGODB_URL

app = Flask(__name__)


def get_collection():
    client = MongoClient(MONGODB_URL)
    return client['bilibili']['new'], client


@app.route('/')
def index():
    col, client = get_collection()
    total = col.count_documents({})

    # Sentiment stats
    pos = col.count_documents({"sentiment_label": "正面"})
    neu = col.count_documents({"sentiment_label": "中性"})
    neg = col.count_documents({"sentiment_label": "负面"})

    # Gender stats
    male = col.count_documents({"user_sex": 1})
    female = col.count_documents({"user_sex": 2})

    # Sentiment-detail samples
    positive_samples = list(col.find(
        {"sentiment_label": "正面"},
        {"comment": 1, "user_name": 1, "sentiment_score": 1, "_id": 0}
    ).sort("sentiment_score", -1).limit(5))

    negative_samples = list(col.find(
        {"sentiment_label": "负面"},
        {"comment": 1, "user_name": 1, "sentiment_score": 1, "_id": 0}
    ).sort("sentiment_score", 1).limit(5))

    client.close()

    return render_template("dashboard.html",
                           total=total, pos=pos, neu=neu, neg=neg,
                           male=male, female=female,
                           positive_samples=positive_samples,
                           negative_samples=negative_samples)


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
    return render_template("gender_pie_chart.html")

@app.route('/top_comments_chart')
def top_comments_chart():
    return render_template("top_comments_chart.html")

@app.route('/top_comments_chart2')
def top_comments_chart2():
    return render_template("top_comments_chart2.html")

@app.route('/user_level_line_chart')
def user_level_line_chart():
    return render_template("user_level_line_chart.html")

@app.route('/wordcloud')
def wordcloud():
    return render_template("wordcloud.html")

@app.route('/wordcloudid')
def wordcloudid():
    return render_template("wordcloudid.html")

@app.route('/level')
def level():
    return render_template("level.html")

@app.route('/comments_show')
def comments_show():
    return render_template("comments_show.html")


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
