from pymongo import MongoClient
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType
from config import MONGODB_URL, TEMPLATES_DIR


def generate_top_reply_chart(num_comments=10):
    try:
        client = MongoClient(MONGODB_URL)
        db = client['bilibili']
        collection = db['new']

        pipeline = [
            {"$group": {"_id": "$comment", "reply_count": {"$max": "$reply_count"}}},
            {"$sort": {"reply_count": -1}},
            {"$limit": num_comments}
        ]

        cursor = collection.aggregate(pipeline)
        comments = []
        reply_counts = []
        for doc in cursor:
            comments.append(doc['_id'])
            reply_counts.append(doc.get('reply_count', 0))

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(comments)
            .add_yaxis("回复数", reply_counts, label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"回复数最高的评论 Top {num_comments}"),
                datazoom_opts=[opts.DataZoomOpts()]
            )
        )

        import os
        output_path = os.path.join(TEMPLATES_DIR, "top_comments_chart2.html")
        bar.render(output_path)
        print(f"Chart saved: {output_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    generate_top_reply_chart(num_comments=10)
