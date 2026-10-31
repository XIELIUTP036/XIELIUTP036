#!/usr/bin/env python3
"""把 .xmind 心智圖印成縮排文字樹，方便對照 data.csv。
用法：python3 tools/xmind_tree.py source/產險名詞大補帖.xmind"""
import json,sys,zipfile
z=zipfile.ZipFile(sys.argv[1]); d=json.loads(z.read('content.json'))
def walk(t,dep=0):
    print('  '*dep+t.get('title','').replace('\n',' / '))
    for c in (t.get('children') or {}).get('attached',[]): walk(c,dep+1)
for s in d: walk(s['rootTopic'])
