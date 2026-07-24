from pymongo import MongoClient
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType
from config import MONGODB_URL, TEMPLATES_DIR


def generate_top_comments_chart(num_comments=10):
    try:
        client = MongoClient(MONGODB_URL)
        db = client['bilibili']
        collection = db['new']

        pipeline = [
            {"$group": {"_id": "$comment", "like_count": {"$max": "$like_count"}}},
            {"$sort": {"like_count": -1}},
            {"$limit": num_comments}
        ]

        cursor = collection.aggregate(pipeline)
        comments = []
        like_counts = []
        for doc in cursor:
            comments.append(doc['_id'])
            like_counts.append(doc.get('like_count', 0))

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(comments)
            .add_yaxis("点赞数", like_counts, label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"点赞数最高的评论 Top {num_comments}"),
                datazoom_opts=[opts.DataZoomOpts()]
            )
        )

        import os
        output_path = os.path.join(TEMPLATES_DIR, "top_comments_chart.html")
        bar.render(output_path)
        print(f"Chart saved: {output_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    generate_top_comments_chart(num_comments=10)
