#!/usr/bin/env python3
"""用法：
  python3 build.py            讀 data.csv → 更新 index.html（資料、noscript 名詞列表、最後更新日期、SEO 標籤、回報連結）
                              並產生 sitemap.xml、robots.txt
  python3 build.py --check    只驗證資料與檢查 index.html 是否已是最新，不寫入任何檔案（CI 用）
網站設定在 site.json：base_url（正式網址，例 https://帳號.github.io/repo）、report_url（回報缺漏名詞表單網址）、google_site_verification（Search Console 驗證碼）、goatcounter（流量分析代碼）。"""
import csv, json, re, sys, html, datetime, os

CHECK = '--check' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
CSV = args[0] if len(args) > 0 else 'data.csv'
PAGE = args[1] if len(args) > 1 else 'index.html'
ROOT = os.path.dirname(os.path.abspath(PAGE))

site = {}
if os.path.exists(os.path.join(ROOT, 'site.json')):
    site = json.load(open(os.path.join(ROOT, 'site.json'), encoding='utf-8'))
BASE = (site.get('base_url') or '').strip().rstrip('/')
REPORT = (site.get('report_url') or '').strip()
GSV = (site.get('google_site_verification') or '').strip()
GC = (site.get('goatcounter') or '').strip()

h = open(PAGE, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="glossary-data">)(.*?)(</script>)', h, re.S)
cats = json.loads(m.group(2))['cats']
rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig', newline='')))
data, seen, errs = [], set(), []
nums = [int(r['id'][2:]) for r in rows if re.fullmatch(r't-\d+', r.get('id', '') or '')]
nxt = max(nums, default=0) + 1
for k, r in enumerate(rows, 2):
    if not any(r.values()): continue
    rid = (r.get('id') or '').strip()
    if not rid: rid = 't-%03d' % nxt; nxt += 1
    if rid in seen: errs.append(f'第{k}列：id 重複（{rid}）')
    seen.add(rid)
    c = r['分類'].strip()
    if c not in cats: errs.append(f'第{k}列：分類「{c}」不在清單內（{"、".join(cats)}）')
    if not r['名詞'].strip(): errs.append(f'第{k}列：缺少名詞')
    if not r['簡述'].strip(): errs.append(f'第{k}列：缺少簡述')
    x = {'n': r['名詞'].strip(), 'a': [a for a in re.split('[、,]', r['別名']) if a.strip()], 'c': c,
         'g': r['群組標籤'].strip(), 's': r['簡述'].strip(), 'd': r['完整說明'].strip()}
    if r['區塊'].strip(): x['sec'] = r['區塊'].strip()
    x['id'] = rid; data.append(x)
for key, val in (('base_url', BASE), ('report_url', REPORT)):
    if val and not re.match(r'https://', val): errs.append(f'site.json：{key} 必須以 https:// 開頭')
if errs: sys.exit('資料有誤，未更新：\n' + '\n'.join(errs))

def put(h, start, end, content):
    """替換 <!--start-->…<!--end--> 之間的內容。"""
    return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: start + content + end, h, flags=re.S)

def body_of(h):
    """比對用：去掉最後更新日期，只看內容是否一致。"""
    return re.sub(r'const UPDATED="[^"]*"', '', h)

out = h
# 1. 名詞資料
js = json.dumps({'cats': cats, 'data': data}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
out = out[:m.start(2)] + js + out[m.end(2):]
# 2. noscript 名詞列表
nos = ('<noscript><p>此頁面需要啟用 JavaScript 才能搜尋與展開說明。以下為名詞列表：</p><ul>'
       + ''.join('<li><strong>%s</strong>：%s</li>' % (html.escape(x['n']), html.escape(x['s'])) for x in data)
       + '</ul></noscript>')
out = put(out, '<!--NOSCRIPT_START-->', '<!--NOSCRIPT_END-->', nos)
# 3. SEO 標籤（網址相關的只在 base_url 有設定時輸出）
desc = re.search(r'<meta name="description" content="([^"]*)">', out).group(1)
seo = ['<link rel="icon" href="favicon.svg" type="image/svg+xml">',
       '<link rel="apple-touch-icon" href="apple-touch-icon.png">',
       '<meta property="og:site_name" content="產險懶人包">',
       '<meta property="og:locale" content="zh_TW">',
       '<meta name="twitter:card" content="summary_large_image">']
if GSV:
    if not re.fullmatch(r'[A-Za-z0-9_-]+', GSV): sys.exit('site.json：google_site_verification 只能是驗證碼本身（content="…" 引號內的文字）')
    seo.append(f'<meta name="google-site-verification" content="{GSV}">')
if BASE:
    seo += [f'<link rel="canonical" href="{BASE}/">',
            f'<meta property="og:url" content="{BASE}/">',
            f'<meta property="og:image" content="{BASE}/og.png">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">']
ld = {'@context': 'https://schema.org', '@type': 'DefinedTermSet', 'name': '產險懶人包', 'description': desc,
      'inLanguage': 'zh-Hant',
      'hasDefinedTerm': [dict({'@type': 'DefinedTerm', 'name': x['n'], 'description': x['s']},
                              **({'url': f"{BASE}/#{x['id']}"} if BASE else {})) for x in data]}
if BASE: ld['url'] = BASE + '/'
seo.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>')
out = put(out, '<!--SEO_START-->', '<!--SEO_END-->', '\n' + '\n'.join(seo) + '\n')
# 3b. 流量分析（GoatCounter，免 Cookie）
if GC and not re.fullmatch(r'[a-z0-9-]+', GC): sys.exit('site.json：goatcounter 只填代碼（例 chanxian），不要整個網址')
ana = (f'\n<script data-goatcounter="https://{GC}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>\n' if GC else '')
out = put(out, '<!--ANALYTICS_START-->', '<!--ANALYTICS_END-->', ana)
# 4. 回報缺漏名詞連結
rep = (f'<p><a href="{html.escape(REPORT)}" target="_blank" rel="noopener">回報缺漏名詞</a></p>' if REPORT else '')
out = put(out, '<!--REPORT_START-->', '<!--REPORT_END-->', rep)

# 5. sitemap.xml、robots.txt
t = datetime.date.today()
files = {}
if BASE:
    files['sitemap.xml'] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                            f'  <url><loc>{BASE}/</loc><lastmod>{t.isoformat()}</lastmod></url>\n'
                            '</urlset>\n')
files['robots.txt'] = 'User-agent: *\nAllow: /\n' + (f'Sitemap: {BASE}/sitemap.xml\n' if BASE else '')

if CHECK:
    stale = []
    if body_of(out) != body_of(h): stale.append(PAGE)
    for name, content in files.items():
        p = os.path.join(ROOT, name)
        old = open(p, encoding='utf-8').read() if os.path.exists(p) else None
        cmp = (lambda s: re.sub(r'<lastmod>[^<]*</lastmod>', '', s or ''))
        if old is None or cmp(old) != cmp(content): stale.append(name)
    if stale: sys.exit('資料正確，但以下檔案不是最新，請執行 python3 build.py：' + '、'.join(stale))
    print(f'檢查通過：{len(data)} 筆，檔案皆為最新')
    sys.exit(0)

out = re.sub(r'const UPDATED="[^"]*"', f'const UPDATED="{t.year}年{t.month}月{t.day}日"', out)
open(PAGE, 'w', encoding='utf-8').write(out)
for name, content in files.items():
    open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(content)
if not BASE and os.path.exists(os.path.join(ROOT, 'sitemap.xml')):
    os.remove(os.path.join(ROOT, 'sitemap.xml'))
print(f'完成：{len(data)} 筆，最後更新 {t}' + ('' if BASE else '（site.json 尚未設定 base_url，略過 sitemap 與網址標籤）')
      + ('' if REPORT else '（未設定 report_url，不顯示回報連結）'))
