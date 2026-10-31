# 產險懶人包

產險名詞教學網頁：搜尋、分類篩選、卡片展開說明。單一靜態頁，無需建置工具。

## 快速開始
```bash
python3 -m http.server 8000   # 開啟 http://localhost:8000
```

## 更新名詞（給維護者）
1. 用 Excel 或 Google 試算表開啟 `data.csv`，新增或修改名詞，存檔時選「CSV UTF-8」。
2. 執行 `python3 build.py`，會更新 `index.html` 內的資料、noscript 名詞列表與最後更新日期。
3. 推送到 GitHub 的 `main` 分支，GitHub Actions 會自動檢查並部署到 GitHub Pages。

## 網站設定（site.json）
| 欄位 | 說明 |
|---|---|
| base_url | 正式網址，例 `https://帳號.github.io/倉庫名`。設定後才會產生 sitemap.xml 與分享用的網址標籤 |
| report_url | 「回報缺漏名詞」表單網址（Google 表單）。留空則頁尾不顯示連結 |

改完 site.json 要再執行一次 `python3 build.py`。

## 第一次部署到 GitHub Pages
1. 在 GitHub 建立倉庫，把這個資料夾推送到 `main`。
2. 倉庫 Settings → Pages → Build and deployment → Source 選「GitHub Actions」。
3. 之後每次推送到 `main` 就會自動更新網站（約 1 分鐘）。
4. 到 Google Search Console 新增網站並提交 `sitemap.xml`。

### 欄位
| 欄位 | 說明 |
|---|---|
| id | 名詞編號 t-001…；新增時留空會自動補。已分享的連結依賴它，請勿更動 |
| 分類 | 商品專區、通用名詞、汽車險、機車險、旅平險、健康傷害險、責任險、住火險、商業火險、工程水險 |
| 區塊 | 分類內的小標題（汽車險／機車險／商品專區使用），其他留空 |
| 群組標籤 | 卡片上的深藍小標籤 |
| 名詞 | 卡片標題；開頭的代碼（如 `59D1`）會自動做成膠囊 |
| 別名 | 多個用「、」分開 |
| 簡述 | 卡片簡述 |
| 完整說明 | 每行以「・」開頭，行首全形空白表示縮排；「例：」「理賠對象：」等自動套用樣式 |

## 文件
- `CLAUDE.md`：給 Claude Code 的專案說明與規則
- `docs/DESIGN.md`：視覺與互動設計規格
- `docs/DATA-MODEL.md`：資料模型與心智圖對應規則
- `docs/DECISIONS.md`：對話中使用者做過的所有決定（依時序）
- `docs/TODO.md`：待辦與待使用者確認事項

## 聲明
本網站內容僅供參考、不構成投保建議，實際保障內容請以保單條款與專業人員說明為準。
