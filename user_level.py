from pymongo import MongoClient
from pyecharts import options as opts
from pyecharts.charts import Line
from pyecharts.globals import ThemeType


def generate_user_level_line_chart():
    try:
        print("=== 脚本开始执行 ===")
        print("=== 开始连接MongoDB ===")
        client = MongoClient('mongodb://DBadmin:123456789@localhost:27017')
        db = client['bilibili']
        collection = db['new']
        print("✅ MongoDB连接成功")

        # 统计不同等级用户的数量
        level_count = {str(i): 0 for i in range(7)}  # 初始化等级计数为0

        cursor = collection.find({}, {'user_level': 1})
        total_count = collection.count_documents({})
        print(f"✅ 成功读取 {total_count} 条用户数据")

        for doc in cursor:
            user_level = str(doc.get('user_level', 'Unknown'))
            if user_level in level_count:
                level_count[user_level] += 1

        # 准备数据
        levels = list(level_count.keys())
        counts = [level_count[level] for level in levels]

        # 创建折线图
        line = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis(levels)
            .add_yaxis("用户数量", counts, is_smooth=True,
                       markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="用户等级分布折线图",
                                          subtitle="共有七个等级：0到6"),
                tooltip_opts=opts.TooltipOpts(trigger="axis")
            )
        )

        # 生成HTML文件
        output_path = "D:/pycharm_xiangmu3/templates/user_level_line_chart.html"
        line.render(output_path)
        print(f"✅ 折线图已生成: {output_path}")

    except Exception as e:
        print(f"❌ 生成图表出错: {e}")

    print("=== 脚本执行结束 ===")


if __name__ == "__main__":
    generate_user_level_line_chart()