from flask import Flask, render_template
from pymongo import MongoClient
from config import MONGODB_URL
from dotenv import load_dotenv
import os, re, time

load_dotenv()

app = Flask(__name__)

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
_ai_client = None
_ai_cache = {}  # {prompt_key: (timestamp, result)}


def _get_ai():
    global _ai_client
    if _ai_client is None and DEEPSEEK_KEY:
        from openai import OpenAI
        _ai_client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com", timeout=8)
    return _ai_client


def _ai_chat(prompt):
    # 缓存 60 秒避免重复调用
    key = prompt[:80]
    now = time.time()
    if key in _ai_cache and now - _ai_cache[key][0] < 60:
        return _ai_cache[key][1]

    client = _get_ai()
    if not client:
        return ""
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=180, temperature=0.7,
        )
        result = resp.choices[0].message.content.strip()
        _ai_cache[key] = (now, result)
        return result
    except:
        return ""


def get_db():
    c = MongoClient(MONGODB_URL)
    return c['bilibili']['new'], c


def analyze(col):
    total = col.count_documents({})
    pos = col.count_documents({"sentiment_label": "正面"})
    neu = col.count_documents({"sentiment_label": "中性"})
    neg = col.count_documents({"sentiment_label": "负面"})
    male = col.count_documents({"user_sex": "男"})
    female = col.count_documents({"user_sex": "女"})

    pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$sentiment_score"}}}]
    r = list(col.aggregate(pipeline))
    avg_score = round(r[0]['avg'] * 100, 1) if r else 50

    pipeline = [
        {"$match": {"like_count": {"$exists": True}}},
        {"$group": {"_id": "$sentiment_label", "avg": {"$avg": "$like_count"}}}
    ]
    likes = {d['_id']: round(d['avg'], 1) for d in col.aggregate(pipeline)}
    pos_likes = likes.get('正面', 0)
    neg_likes = likes.get('负面', 0)

    pipeline = [{"$group": {"_id": "$user_name", "cnt": {"$sum": 1}}}, {"$sort": {"cnt": -1}}, {"$limit": 3}]
    top_users = [{"name": u['_id'], "count": u['cnt']} for u in col.aggregate(pipeline)]

    pos_pct = round(pos / total * 100, 1) if total else 0
    users_str = '、'.join(u['name'] for u in top_users)

    # AI 摘要（DeepSeek 优先，规则降级）
    summary = _ai_chat(
        f"分析B站评论数据：共{total}条，正面{pos}条({pos_pct}%)，中性{neu}条，负面{neg}条。"
        f"平均情感得分{avg_score}%。正面评论平均{pos_likes}赞，负面{neg_likes}赞。"
        f"活跃用户：{users_str}。用不超过100字中文给出数据洞察。"
    )
    if not summary:
        if pos_pct > 65:
            summary = f"整体评论偏正面（{pos_pct}%），社区氛围良好。正面评论平均 {pos_likes} 赞，高于负面评论的 {neg_likes} 赞。"
        elif pos_pct > 45:
            summary = f"评论情感分布均衡（正面 {pos_pct}%）。活跃用户 {users_str} 参与度最高。"
        else:
            summary = f"负面评论占比较高，存在讨论分歧。活跃用户包括 {users_str}，建议关注他们的反馈。"

    return {
        "total": total, "pos": pos, "neu": neu, "neg": neg,
        "male": male, "female": female, "avg_score": avg_score,
        "pos_pct": pos_pct, "pos_likes": pos_likes, "neg_likes": neg_likes,
        "top_users": top_users, "summary": summary,
    }


@app.route('/')
def index():
    col, client = get_db()
    data = analyze(col)
    pos_samples = list(col.find({"sentiment_label": "正面"}, {"comment": 1, "user_name": 1, "sentiment_score": 1})
                       .sort("sentiment_score", -1).limit(4))
    neg_samples = list(col.find({"sentiment_label": "负面"}, {"comment": 1, "user_name": 1, "sentiment_score": 1})
                       .sort("sentiment_score", 1).limit(4))
    client.close()
    return render_template("zhuye.html", **data, pos_samples=pos_samples, neg_samples=neg_samples, active_page="home")


@app.route('/<page>')
def chart_page(page):
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
    chart_path = os.path.join(app.root_path, app.template_folder, filename)

    chart_html = ""
    if os.path.exists(chart_path):
        with open(chart_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        head_scripts = ""
        if '<head>' in raw and '</head>' in raw:
            head = raw.split('<head>')[1].split('</head>')[0]
            head_scripts = '\n'.join(
                re.findall(r'<script[^>]*>.*?</script>', head, re.DOTALL) +
                re.findall(r'<script[^>]*/>', head)
            )
        body = raw
        if '<body>' in body:
            body = body.split('<body>')[1]
        if '</body>' in body:
            body = body.split('</body>')[0]
        chart_html = head_scripts + '\n' + body

    col, client = get_db()
    data = analyze(col)
    client.close()

    # DeepSeek AI 分析这个图表
    insight = _ai_chart_insight(page, data)
    return render_template("chart_page.html", title=title, chart_html=chart_html,
                           data=data, insight=insight, active_page=page)


def _ai_chart_insight(page, data):
    """DeepSeek 分析图表数据，降级为规则模板"""
    prompts = {
        "top_comments_chart": f"分析B站评论数据：点赞最高10条评论。正面{data['pos_pct']}%，正面评论均赞{data['pos_likes']}，负面均赞{data['neg_likes']}。用60字中文总结。",
        "top_comments_chart2": f"分析B站评论数据：回复数最高10条评论，共{data['total']}条。高回复意味着热议话题。用60字中文总结。",
        "gender_pie_chart": f"分析B站用户性别数据：男{data['male']}人，女{data['female']}人，共{data['total']}评论。用60字中文分析受众结构。",
        "user_level_line_chart": f"分析B站用户等级分布，共{data['total']}条评论。用60字中文分析用户质量和活跃度。",
        "wordcloud": f"B站评论词云分析：共{data['total']}条评论生成的词云。正面{data['pos_pct']}%。用60字中文总结讨论焦点。",
        "wordcloudid": f"B站用户名词云分析：共{data['total']}用户名的词云。活跃用户{','.join(u['name'] for u in data['top_users'][:3])}。用60字中文总结。",
    }
    prompt = prompts.get(page, "")
    result = _ai_chat(prompt) if prompt else ""
    return result if result else _fallback_insight(page, data)


def _fallback_insight(page, data):
    if page == "wordcloud":
        return f"从 {data['total']} 条评论中提取的高频关键词。正面评论占 {data['pos_pct']}%，热词反映了观众对内容的关注焦点。"
    if page == "wordcloudid":
        return f"活跃用户如 {data['top_users'][0]['name']} 等构成了社区的核心互动群体。"
    if page == "gender_pie_chart":
        return f"参与评论的用户中男性 {data['male']} 人、女性 {data['female']} 人。性别分布反映了该视频的受众结构。"
    if page == "user_level_line_chart":
        return f"高等级用户通常意味着更活跃的社区参与度和更高的内容消费深度。"
    if page == "top_comments_chart":
        return f"点赞最高 10 条评论代表了观众最认同的观点。正面评论平均 {data['pos_likes']} 赞，高于负面评论的 {data['neg_likes']} 赞。"
    if page == "top_comments_chart2":
        return f"回复数最高 10 条评论引发了较多讨论互动，是话题的引爆点。"
    return ""


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
