from pymongo import MongoClient
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.globals import ThemeType


def user_sex():
    try:
        # 连接到MongoDB
        client = MongoClient('mongodb://DBadmin:123456789@localhost:27017/')
        db = client['bilibili']
        collection = db['new']
        print("✅ MongoDB连接成功")

        # 查询数据并统计性别信息
        gender_count = {}
        cursor = collection.find({}, {'user_sex': 1})

        for doc in cursor:
            user_sex = doc.get('user_sex', 'Unknown')
            gender_count[user_sex] = gender_count.get(user_sex, 0) + 1

        # 准备数据
        genders = list(gender_count.keys())
        gender_nums = [gender_count[gender] for gender in genders]

        # 创建饼图
        pie = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add("", [list(z) for z in zip(genders, gender_nums)])
            .set_global_opts(title_opts=opts.TitleOpts(title="用户性别分布饼图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )

        # 生成HTML文件
        output_path = "D:/pycharm_xiangmu3/templates/gender_pie_chart.html"
        pie.render(output_path)
        print(f"✅ 图表已生成: {output_path}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


if __name__ == '__main__':
    print("=== 脚本开始执行 ===")
    user_sex()
    print("=== 脚本执行结束 ===")