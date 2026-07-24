import os, sys
sys.path.insert(0,'.')
from app import app

with app.test_client() as c:
    r = c.get('/wordcloud')
    body = r.data.decode()
    # Find chart_html content 
    idx = body.find('chart-box')
    section = body[idx:idx+300]
    print("Chart box section:")
    print(section)
    print()
    print("--- full body end ---")
    print(body[-500:])
