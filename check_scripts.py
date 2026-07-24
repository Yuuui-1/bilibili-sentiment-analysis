import re
with open('D:/2025.6.26.yzx.bilibili/templates/wordcloud.html', encoding='utf-8') as f:
    raw = f.read()
head = raw.split('<head>')[1].split('</head>')[0]

# Find all script tags with src
src_scripts = re.findall(r'<script[^>]*src="([^"]*)"[^>]*></script>', head)
print("Script src tags:", src_scripts)

# Find all script tags (inline)
inline = re.findall(r'<script[^>]*>', head)
print("Script tags:", len(inline))
for s in inline[:5]:
    print(" ", s[:100])
