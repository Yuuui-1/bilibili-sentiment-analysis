from pymongo import MongoClient

c = MongoClient('mongodb://localhost:27017')
col = c['bilibili']['new']

# Check raw values
docs = list(col.find({}, {'user_sex': 1, 'user_name': 1}).limit(10))
for d in docs:
    sex = d.get('user_sex')
    print(f"  name={d.get('user_name')} sex={repr(sex)}")

# Direct count queries  
for label in ['男', '女', '保密']:
    count = col.count_documents({'user_sex': label})
    print(f"{label}: {count}")

# Try numeric
for val in [0, 1, 2]:
    count = col.count_documents({'user_sex': val})
    print(f"user_sex={val}: {count}")
