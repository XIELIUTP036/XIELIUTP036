# CLAUDE.md：產險懶人包

給 Claude Code 的專案說明。開始工作前請先讀完這份，再依需要看 `docs/` 內的文件。

## 專案是什麼
「產險懶人包」是一個**產險名詞教學網頁**：搜尋框、分類標籤（含筆數）、三欄圓角卡片（名詞／別名／簡述），點卡片展開完整說明。
- **主要功能是「教學」**：內容要反覆閱讀，所以不加浮水印、不做會干擾閱讀的裝飾。
- 版面參考「保險克勞斯」的名詞百科頁（只參考版面結構，不使用其名稱、Logo 與文案）。
- 內容來源是使用者自己的心智圖 `source/產險名詞大補帖.xmind`（附 `source/mindmap-*.jpeg|png` 截圖）。
- **正式網站**：https://xieliutp036.github.io/XIELIUTP036/ （GitHub 倉庫 `XIELIUTP036/XIELIUTP036`，推送 `main` 自動部署）
- 目前為單一靜態頁（無框架、無建置工具），已用 Claude 的 artifact 託管預覽過：
  - https://claude.ai/artifact/2dRPKWLMfLRZVUNotfiaUc（最新，2026-10-31，內容同 `index.html`）
  - https://claude.ai/artifact/TuzjbjE6y6rAgMnVmhfLo4（舊版，聊天室建立）

## 目錄結構
```
index.html        頁面本體（HTML+CSS+JS，資料內嵌於 <script id="glossary-data">）
data.csv          名詞資料的「唯一事實來源」，用 Excel/試算表編輯（UTF-8 BOM）
build.py          讀 data.csv → 寫回 index.html 的資料、<noscript> 名詞列表、最後更新日期、SEO 標籤、回報連結；產生 sitemap.xml、robots.txt
site.json         網站設定：base_url（正式網址）、report_url（回報缺漏名詞表單）
favicon.svg、apple-touch-icon.png、og.png   網站圖示與社群分享預覽圖（tools/make_images.js 產生）
.github/workflows/pages.yml   推送到 main 自動部署 GitHub Pages（只部署網站檔案，不含 source/、docs/、data.csv）
source/           原始心智圖（.xmind）與截圖——**不放進 GitHub 倉庫**（.gitignore 排除；2026-10-31 前的提交紀錄裡仍有），只存在使用者本機
tools/xmind_tree.py   把 .xmind 印成縮排文字樹，方便對照資料
docs/             設計、資料模型、決策紀錄、待辦
```

## 常用指令
```bash
python3 build.py                 # 更新資料與「最後更新日期」（日期取當天）
python3 build.py --check         # 只檢查不寫入（GitHub Actions 部署前會跑；改了 CSV 卻沒 build 會擋下部署）
node tools/make_images.js        # 重新產生 apple-touch-icon.png、og.png（改圖示或網站描述時）
python3 tools/xmind_tree.py source/產險名詞大補帖.xmind   # 檢視心智圖結構
python3 -m http.server 8000      # 本機預覽（或直接開 index.html）
```
`build.py` 會檢查：id 重複、分類不在清單內、缺名詞、缺簡述；有錯就列出並**不更新**。

## 硬性規則（務必遵守）
1. **未經使用者要求，不要改動任何文字內容**（名詞、別名、簡述、完整說明、頁尾聲明）。設計優化只能動版面／樣式／互動。
2. **`data.csv` 是事實來源**。不要直接手改 `index.html` 內的 JSON 資料；改 CSV 後跑 `build.py`。
   - 資料已在對話中經過大量人工指定的修改，**不能**再用 xmind 重新轉出來覆蓋（會洗掉修改）。xmind 只用來對照與補資料。
3. **`id`（t-001…）不可更動、不可重複使用**：卡片連結 `#t-020` 依賴它。新增名詞 id 留空，build.py 會自動補號。
4. 分類必須是下列十個之一，順序固定：`商品專區、通用名詞、汽車險、機車險、旅平險、健康傷害險、責任險、住火險、商業火險、工程水險`（「全部」是前端自動加的，固定在最前）。順序存在 `index.html` 的 `"cats"`；顏色與網址代稱依分類名稱對應（`CC`、`SL`），改順序不影響連結與顏色。
5. 頁尾聲明「本網站內容僅供參考、不構成投保建議，實際保障內容請以保單條款與專業人員說明為準」與「最後更新日期」必須保留。
6. 不加浮水印（使用者已明確決定）。
7. 說明文字有一部分是 AI 依心智圖補寫，保險條款、額度、理賠規則須由專業人員覆核；不要自行新增未經使用者提供的法規或數字。
8. 使用者用繁體中文（台灣用語）溝通，回覆與註解請用繁體中文。

## 資料模型（摘要，詳見 docs/DATA-MODEL.md）
CSV 欄位：`id, 分類, 區塊, 群組標籤, 名詞, 別名, 簡述, 完整說明`
- 「完整說明」每行以 `・` 開頭，行首全形空白代表縮排；`例：`、`理賠對象：`、`理賠項目：`、`承保範圍：`、`自負額：`、`啟動時間點：`、`投保限制：`、`保障範圍：`、`保障項目：`、`服務項目：`、`加值選：`、`承保對象：` 會被前端自動轉成樣式。
- 「區塊」：汽車險、機車險、商品專區用來在分類內再分小標題；其他分類留空。
- 「群組標籤」：卡片上的深藍小標籤。

## 前端重點（詳見 docs/DESIGN.md）
- 單檔、無相依套件；只載入 Google Fonts（Noto Sans TC）。
- 深藍主色；每個分類有自己的輔助色（`--c0…--c9`，亮／暗兩組，已實測對比度）。
- 搜尋：名詞>群組/別名>簡述>內文的相關度排序、同義詞（`SYN`）、命中標示、內文命中自動展開、中文輸入法選字期間不重繪。
- 路由：`#all`、`#cat-<slug>`、`#t-###`；`hashchange` 驅動。
- 無障礙：標題是 `button`＋`aria-expanded`、標籤 `aria-pressed`、結果筆數 `aria-live`、`prefers-reduced-motion`、焦點樣式。
- 淺色／深色／跟隨系統三段切換（存 localStorage，需 try/catch）。
- 列印樣式（自動展開全部、隱藏操作鈕、兩欄）。
- 分類列可左右滑動：手機觸控滑動；桌機有左右箭頭鈕、滑鼠拖曳、滾輪橫移；兩側漸層提示還有更多。

## 已知待辦與待使用者決定（詳見 docs/TODO.md）
- 三張「（內容建置中）」卡片（健康傷害險、工程險、水險/運輸險）：使用者決定先照目前樣式顯示，之後再補內容。
- 正式上線（2026-10-31 開始）：使用者選 GitHub Pages、先用免費網址；第一階段做基本 SEO＋回報缺漏名詞連結。**已上線（2026-10-31）**；待使用者提供 Google 表單網址、到 Google Search Console 提交 sitemap。
- 之後可做：每個名詞獨立頁面、自訂網域、流量分析、字體自行託管。

## 工作方式偏好
- 使用者偏好小步迭代：每次改一組項目，改完說明「改了什麼、哪裡沒動、有何不確定」。
- 遇到使用者文字與心智圖不一致（如「閩中騷擾」vs「民眾騷擾」、「健康守護家」vs「健康守護加」、「依附人員責任險」vs「護理人員責任險」），先採心智圖用字並在回覆中明說，再讓使用者確認。
