from pymongo import MongoClient
import jieba
from pyecharts.charts import WordCloud
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from config import MONGODB_URL, TEMPLATES_DIR

CHINESE_STOPWORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
])


def get_username_data():
    client = MongoClient(MONGODB_URL)
    db = client['bilibili']
    collection = db['new']
    cursor = collection.find({}, {"user_name": 1, "_id": 0})
    texts = [doc['user_name'] for doc in cursor if 'user_name' in doc]
    client.close()
    return texts


def generate_username_wordcloud():
    texts = get_username_data()
    if not texts:
        print("No username data found")
        return

    all_text = " ".join(texts)
    words = jieba.lcut(all_text)
    filtered = [w.strip() for w in words if len(w.strip()) > 1 and w.strip() not in CHINESE_STOPWORDS]

    from collections import Counter
    word_counts = Counter(filtered).most_common(100)

    wc = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add("", word_counts, word_size_range=[12, 60], shape="circle")
        .set_global_opts(title_opts=opts.TitleOpts(title="用户名词云"))
    )

    import os
    output_path = os.path.join(TEMPLATES_DIR, "wordcloudid.html")
    wc.render(output_path)
    print(f"Username word cloud saved: {output_path}")


if __name__ == "__main__":
    generate_username_wordcloud()
