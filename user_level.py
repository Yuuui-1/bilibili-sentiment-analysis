from pymongo import MongoClient
from pyecharts import options as opts
from pyecharts.charts import Line, Pie
from pyecharts.globals import ThemeType
from config import MONGODB_URL, TEMPLATES_DIR


def generate_level_chart():
    try:
        client = MongoClient(MONGODB_URL)
        db = client['bilibili']
        collection = db['new']

        pipeline = [
            {"$group": {"_id": "$user_level", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        cursor = collection.aggregate(pipeline)
        levels = []
        counts = []
        for doc in cursor:
            levels.append(str(doc['_id']))
            counts.append(doc['count'])

        line = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(levels)
            .add_yaxis("用户数", counts, is_smooth=True)
            .set_global_opts(title_opts=opts.TitleOpts(title="用户等级分布"))
        )

        import os
        output_path = os.path.join(TEMPLATES_DIR, "user_level_line_chart.html")
        line.render(output_path)
        print(f"Chart saved: {output_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    generate_level_chart()
