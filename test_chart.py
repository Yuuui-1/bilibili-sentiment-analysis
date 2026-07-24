import re, os
path = 'D:/2025.6.26.yzx.bilibili/templates/wordcloud.html'
with open(path, encoding='utf-8') as f:
    raw = f.read()

head = raw.split('<head>')[1].split('</head>')[0] if '<head>' in raw else ''
extracted = re.findall(r'<script[^>]*>.*?</script>', head, re.DOTALL) + re.findall(r'<script[^>]*/>', head)
print("Extracted scripts:", len(extracted))
for s in extracted:
    print(" ", s[:100], "..." if len(s)>100 else "")

# Now test via Flask
import sys; sys.path.insert(0,'.')
from app import app
with app.test_client() as c:
    r = c.get('/wordcloud')
    body = r.data.decode()
    has_echarts_cdn = 'assets.pyecharts.org' in body or 'echarts.min.js' in body
    print(f"\nFlask response has echarts CDN: {has_echarts_cdn}")
    has_init = 'echarts.init' in body
    print(f"Has echarts.init: {has_init}")
