from pymongo import MongoClient
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.globals import ThemeType
from config import MONGODB_URL, TEMPLATES_DIR


def generate_gender_pie_chart():
    try:
        client = MongoClient(MONGODB_URL)
        db = client['bilibili']
        collection = db['new']

        pipeline = [
            {"$group": {"_id": "$user_sex", "count": {"$sum": 1}}},
        ]
        cursor = collection.aggregate(pipeline)
        data = []
        for doc in cursor:
            label = {0: "未知", 1: "男", 2: "女"}.get(doc['_id'], str(doc['_id']))
            data.append([label, doc['count']])

        pie = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add("性别", data)
            .set_global_opts(title_opts=opts.TitleOpts(title="用户性别分布"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )

        import os
        output_path = os.path.join(TEMPLATES_DIR, "gender_pie_chart.html")
        pie.render(output_path)
        print(f"Chart saved: {output_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    generate_gender_pie_chart()
