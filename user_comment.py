from pymongo import MongoClient
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType


def generate_top_comments_chart(num_comments=10):
    try:
        print("=== 脚本开始执行 ===")
        print("=== 开始连接MongoDB ===")
        client = MongoClient('mongodb://DBadmin:123456789@localhost:27017')
        db = client['bilibili']
        collection = db['new']
        print("✅ MongoDB连接成功")

        # 聚合查询并去重
        pipeline = [
            {"$group": {"_id": "$comment", "apprecate_count": {"$max": "$apprecate_count"}}},
            {"$sort": {"apprecate_count": -1}},
            {"$limit": num_comments}
        ]

        cursor = collection.aggregate(pipeline)
        print(f"✅ 成功聚合 {num_comments} 条评论数据")

        # 准备数据
        comments = []
        appreciate_counts = []
        for doc in cursor:
            comments.append(doc['_id'])
            appreciate_counts.append(doc['apprecate_count'])

        # 创建柱状图
        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(comments)
            .add_yaxis("点赞数", appreciate_counts, label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"点赞数最高的评论 Top {num_comments}",
                                          subtitle="从MongoDB读取数据并去重"),
                datazoom_opts=[opts.DataZoomOpts()]
            )
        )

        # 生成HTML文件
        output_path = "D:/pycharm_xiangmu3/templates/top_comments_chart.html"
        bar.render(output_path)
        print(f"✅ 柱状图已生成: {output_path}")

    except Exception as e:
        print(f"❌ 生成图表出错: {e}")

    print("=== 脚本执行结束 ===")


if __name__ == "__main__":
    generate_top_comments_chart(num_comments=30)