from pymongo import MongoClient
from snownlp import SnowNLP
from config import MONGODB_URL


def analyze_sentiment():
    """遍历 MongoDB 中的评论，添加情感得分字段"""
    client = MongoClient(MONGODB_URL)
    db = client['bilibili']
    collection = db['new']

    docs = collection.find({"sentiment_score": {"$exists": False}})
    count = 0
    for doc in docs:
        try:
            text = doc.get('comment', '')
            s = SnowNLP(text)
            score = round(s.sentiments, 3)  # 0-1, 越接近1越正面
            label = "正面" if score > 0.6 else "中性" if score > 0.4 else "负面"
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"sentiment_score": score, "sentiment_label": label}}
            )
            count += 1
        except Exception as e:
            print(f"Error processing: {e}")

    client.close()
    print(f"Analyzed {count} comments for sentiment")


if __name__ == "__main__":
    analyze_sentiment()
