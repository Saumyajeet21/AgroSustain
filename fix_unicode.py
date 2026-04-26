import re

path = r'f:\Minor_Project\backend\ml\train_resnet50.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Replace unicode with ASCII
replacements = {
    '\u2014': '-', '\u2013': '-', '\u2500': '-', '\u2502': '|',
    '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
    '\u2713': 'OK', '\u2714': 'OK', '\u2718': 'X',
    '\u2588': '#', '\u2591': '.', '\u25b6': '>>', '\u23f3': 'ETA',
    '\u23f1': 'TIMER', '\u2705': '[OK]', '\u26a0': '[WARN]',
    '\u00d7': 'x', '\u00b1': '+/-',
}
for uni, asc in replacements.items():
    content = content.replace(uni, asc)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - all unicode replaced.')
