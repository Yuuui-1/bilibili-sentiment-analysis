import requests
import pymongo
import time
import os
from pymongo import MongoClient
from datetime import datetime
from config import MONGODB_URL


class BCommentParse(object):
    def __init__(self, base_url):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Cookie': os.getenv('BILIBILI_COOKIE', 'your_bilibili_cookie_here'),

        }
        self.base_url = base_url
        self.min_comments = 30  # 最少获取30条评论

    def my_init(self):
        id = self.base_url.split('video/')[-1].split('?')[0]
        if id.startswith('av'):
            id = id.split('av')[-1]
            self.oid = self.get_avid_title(id)
        else:
            self.oid = self.get_avid_title(id, av=False)
        self.set_page()

    def get_avid_title(self, id_number, av=True):
        if av:
            api = f'https://api.bilibili.com/x/web-interface/view?aid={id_number}'
        else:
            api = f'https://api.bilibili.com/x/web-interface/view?bvid={id_number}'
        r = requests.get(api, headers=self.headers)
        data = r.json()
        self.video_title = data['data']['title']
        return data['data']['aid']

    def set_page(self):
        try:
            self.client = MongoClient(MONGODB_URL)
            self.collection = self.client["bilibili"]["new"]  # 存储到new集合
            # 在set_page方法中添加（只需执行一次）
            self.collection.create_index([("user_id", 1), ("comment", 1)], unique=True)
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise

    def parse_comment(self):
        self.my_init()
        base_url = f'https://api.bilibili.com/x/v2/reply?type=1&oid={self.oid}&sort=0'  # 按时间排序获取更多评论
        page = 1
        total_comments = 0

        while total_comments < self.min_comments:
            try:
                url = f"{base_url}&pn={page}"
                print(f"🔍 正在请求第{page}页: {url}")

                response = requests.get(url, headers=self.headers)
                data = response.json()

                # 检查API返回状态
                if data.get('code') != 0:
                    print(f"⚠️ API返回错误: {data.get('message')}")
                    break

                replies = data.get('data', {}).get('replies', [])
                if not replies:
                    print(f"✅ 已爬取所有评论，共{total_comments}条")
                    break

                print(f"📄 第{page}页获取到{len(replies)}条评论")

                for comment in replies:
                    # 提取用户信息
                    member = comment.get('member', {})
                    content = comment.get('content', {})

                    item = {
                        'user_id': member.get('mid'),
                        'user_name': member.get('uname'),
                        'user_sex': member.get('sex', '未知'),
                        'user_level': member.get('level_info', {}).get('current_level', 0),
                        'user_is_vip': '是' if member.get('vip', {}).get('vipStatus') == 1 else '否',
                        'like_count': comment.get('like', 0),
                        'reply_count': comment.get('rcount', 0),
                        'comment': content.get('message', ''),
                        'comment_time': datetime.fromtimestamp(comment.get('ctime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                        'video_id': self.oid,
                        'video_title': self.video_title,
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # 去重检查
                    if not self.collection.find_one({
                        'user_id': item['user_id'],
                        'comment': item['comment']
                    }):
                        self.collection.insert_one(item)
                        total_comments += 1
                        print(
                            f"💾 已存储 {total_comments}/30 条 | 用户: {item['user_name']} (Lv.{item['user_level']}, 性别:{item['user_sex']})")

                        if total_comments >= self.min_comments:
                            break
                    else:
                        print("🔄 跳过重复评论")

                page += 1
                time.sleep(1.5)  # 增加延迟防止被封

            except Exception as e:
                print(f"❌ 发生错误: {e}")
                break

        print(f"\n✅ 任务完成！共获取 {total_comments} 条评论")
        if total_comments < self.min_comments:
            print(f"⚠️ 注意: 仅获取到 {total_comments} 条评论，未达到目标 {self.min_comments} 条")


if __name__ == '__main__':
    video_url = 'https://www.bilibili.com/video/BV19Q7UzXE1v'  # 替换为目标视频URL
    if video_url.startswith('https://www.bilibili.com/video/'):
        print("=== B站评论爬虫启动 ===")
        b = BCommentParse(video_url)
        b.parse_comment()
    else:
        print("❌ 无效的视频URL，请以https://www.bilibili.com/video/开头")