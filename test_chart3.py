import os, sys
sys.path.insert(0,'.')
from app import app

path = os.path.join(app.template_folder, "wordcloud.html")
print("Looking for:", path)
print("Exists:", os.path.exists(path))
print("template_folder:", app.template_folder)

if os.path.exists(path):
    with open(path, encoding='utf-8') as f:
        raw = f.read()
    print("File size:", len(raw))
    print("Has <head>:", '<head>' in raw)
    print("Has <body>:", '<body>' in raw)
