#!/usr/bin/env python3
"""用法：python3 build.py [data.csv] [index.html]
讀取 data.csv，更新 index.html 內的名詞資料、noscript 名詞列表與「最後更新日期」。"""
import csv,json,re,sys,html,datetime
CSV=sys.argv[1] if len(sys.argv)>1 else 'data.csv'
PAGE=sys.argv[2] if len(sys.argv)>2 else 'index.html'
h=open(PAGE,encoding='utf-8').read()
m=re.search(r'(<script type="application/json" id="glossary-data">)(.*?)(</script>)',h,re.S)
cats=json.loads(m.group(2))['cats']
rows=list(csv.DictReader(open(CSV,encoding='utf-8-sig',newline='')))
data,seen,errs=[],set(),[]
nums=[int(r['id'][2:]) for r in rows if re.fullmatch(r't-\d+',r.get('id','') or '')]
nxt=max(nums,default=0)+1
for k,r in enumerate(rows,2):
    if not any(r.values()): continue
    rid=(r.get('id') or '').strip()
    if not rid: rid='t-%03d'%nxt; nxt+=1
    if rid in seen: errs.append(f'第{k}列：id 重複（{rid}）')
    seen.add(rid)
    c=r['分類'].strip()
    if c not in cats: errs.append(f'第{k}列：分類「{c}」不在清單內（{"、".join(cats)}）')
    if not r['名詞'].strip(): errs.append(f'第{k}列：缺少名詞')
    if not r['簡述'].strip(): errs.append(f'第{k}列：缺少簡述')
    x={'n':r['名詞'].strip(),'a':[a for a in re.split('[、,]',r['別名']) if a.strip()],'c':c,'g':r['群組標籤'].strip(),'s':r['簡述'].strip(),'d':r['完整說明'].strip()}
    if r['區塊'].strip(): x['sec']=r['區塊'].strip()
    x['id']=rid; data.append(x)
if errs: sys.exit('資料有誤，未更新：\n'+'\n'.join(errs))
js=json.dumps({'cats':cats,'data':data},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
h=h[:m.start(2)]+js+h[m.end(2):]
nos='<!--NOSCRIPT_START--><noscript><p>此頁面需要啟用 JavaScript 才能搜尋與展開說明。以下為名詞列表：</p><ul>'+''.join('<li><strong>%s</strong>：%s</li>'%(html.escape(x['n']),html.escape(x['s'])) for x in data)+'</ul></noscript><!--NOSCRIPT_END-->'
h=re.sub(r'<!--NOSCRIPT_START-->.*?<!--NOSCRIPT_END-->',lambda _:nos,h,flags=re.S)
t=datetime.date.today();h=re.sub(r'const UPDATED="[^"]*"',f'const UPDATED="{t.year}年{t.month}月{t.day}日"',h)
open(PAGE,'w',encoding='utf-8').write(h)
print(f'完成：{len(data)} 筆，最後更新 {t}')
