from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template("zhuye.html")

@app.route('/china')
def china():
    return render_template("sex.html")

@app.route('/gender_pie_chart')
def gender_pie_chart():
    return render_template("gender_pie_chart.html")

@app.route('/china02')
def china02():
    return render_template("like.html")

@app.route('/top_comments_chart')
def top_comments_chart():
    return render_template("top_comments_chart.html")

@app.route('/china03')
def china03():
    return render_template("reply.html")

@app.route('/top_comments_chart2')
def top_comments_chart2():
    return render_template("top_comments_chart2.html")

@app.route('/china04')
def china04():
    return render_template("level.html")

@app.route('/user_level_line_chart')
def user_level_line_chart():
    return render_template("user_level_line_chart.html")

@app.route('/china05')
def china05():
    return render_template("comments_show.html")

@app.route('/wordcloud')
def wordcloud():
    return render_template("wordcloud.html")

@app.route('/china06')
def china06():
    return render_template("id_show.html")

@app.route('/wordcloudid')
def wordcloudid():
    return render_template("wordcloudid.html")

@app.route('/index')
def index():
    return render_template("zhuye.html")


if __name__ == '__main__':
    app.run()
