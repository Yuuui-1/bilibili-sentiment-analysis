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
    "什么", "怎么", "如果", "因为", "所以", "但是", "然后", "可以", "这个",
    "那个", "真的", "觉得", "感觉", "知道", "喜欢", "还是", "应该", "已经",
    "不是", "就是", "只是", "的话", "吧", "吗", "呢", "啊", "哦", "嗯",
    "哈哈", "哈哈哈", "哈哈哈哈",
])


def get_comment_data():
    client = MongoClient(MONGODB_URL)
    db = client['bilibili']
    collection = db['new']
    cursor = collection.find({}, {"comment": 1, "_id": 0})
    texts = [doc['comment'] for doc in cursor if 'comment' in doc]
    client.close()
    return texts


def generate_word_cloud():
    texts = get_comment_data()
    if not texts:
        print("No comment data found")
        return

    all_text = " ".join(texts)
    words = jieba.lcut(all_text)
    filtered = [w.strip() for w in words if len(w.strip()) > 1 and w.strip() not in CHINESE_STOPWORDS]

    from collections import Counter
    word_counts = Counter(filtered).most_common(100)

    wc = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add("", word_counts, word_size_range=[12, 60], shape="circle")
        .set_global_opts(title_opts=opts.TitleOpts(title="评论词云"))
    )

    import os
    output_path = os.path.join(TEMPLATES_DIR, "wordcloud.html")
    wc.render(output_path)
    print(f"Word cloud saved: {output_path}")


if __name__ == "__main__":
    generate_word_cloud()
