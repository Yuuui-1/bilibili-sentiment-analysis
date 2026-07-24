from pymongo import MongoClient
from collections import Counter
import jieba
from wordcloud import WordCloud
from pyecharts import options as opts
from pyecharts.charts import WordCloud
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')


def get_shortnote_data():
    try:
        print("=== 开始连接MongoDB ===")
        client = MongoClient('mongodb://DBadmin:123456789@localhost:27017')
        db = client['bilibili']
        collection = db['new']
        print("✅ MongoDB连接成功")

        # 从 MongoDB 中读取数据
        data = collection.find({}, {"_id": 0, "comment": 1})
        print(f"✅ 成功读取 {collection.count_documents({})} 条数据")

        # 提取 shortnote 数据
        shortnotes = [d["comment"] for d in data]
        return shortnotes

    except Exception as e:
        print(f"❌ 数据库操作出错: {e}")
        return []


def generate_word_cloud(shortnotes):
    try:
        # 合并所有 shortnote 文本
        text = ' '.join(shortnotes)

        # 使用 jieba 分词
        words = jieba.lcut(text)

        # 过滤掉单个字和停用词
        filtered_words = [word for word in words if len(word) > 1 and word not in stopwords.words('english')]

        # 统计词频
        word_counts = Counter(filtered_words)

        # 生成词云图
        wordcloud = (
            WordCloud()
            .add(series_name="", data_pair=word_counts.items(), word_size_range=[20, 100])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="评论内容词云图"),
                tooltip_opts=opts.TooltipOpts(is_show=True),
            )
        )

        # 保存为 HTML 文件
        output_path = "D:/pycharm_xiangmu3/templates/wordcloud.html"
        wordcloud.render(output_path)
        print(f"✅ 词云图已生成: {output_path}")

    except Exception as e:
        print(f"❌ 生成词云图出错: {e}")


def main():
    print("=== 脚本开始执行 ===")
    # 获取 shortnote 数据
    shortnotes = get_shortnote_data()

    if shortnotes:
        # 生成词云图并保存为 HTML
        generate_word_cloud(shortnotes)
    else:
        print("❌ 未获取到有效数据，终止执行")

    print("=== 脚本执行结束 ===")


if __name__ == "__main__":
    main()