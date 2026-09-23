# 太陽光電電廠 8D 異常診斷決策管理門戶 (Solar 8D Diagnostic Hub)

本系統為專為太陽光電維運團隊、機電工程師與電廠資產擁有者打造的 **8D 異常診斷決策管理門戶**。支援每年 **100+ 份** 診斷報告之規模化管理、多維檢索、戰情統計、既有 GitHub Pages 報告外跳連結，並與 **Supabase 雲端資料庫及 Storage 存儲桶** 深度結合，提供文字與現場照片拖拉直傳功能。

---

## 🌟 核心功能亮點

1. **戰情總覽儀表板 (Executive Cockpit)**：
   - 4 大即時列管狀態卡片：累計案場數、D0~D4 調查圍堵中（紅標）、D5~D7 對策驗證中（黃標）、D8 已結案歸檔（綠標）。
   - 財務量化橫幅：即時統計全場**累計年化損失金額 (NT$ 萬)** 與**短少發電度數 (kWh)**。
2. **多維檢索與過濾體系 (針對每年 100+ 份報告設計)**：
   - **即時模糊搜尋**：案號代碼 (如 `PV-2026-DA01`)、電廠名稱、異常設備 (如 `INV-13`)、根本原因關鍵字。
   - **多維交叉篩選**：8D 階段狀態、嚴重等級 (Level 1~4)、年度歸檔 (2026/2025/2024...)、案場型態 (水上浮體/地面/屋頂/漁電共生)。
   - **雙重視圖模式**：可自由切換「網格視覺卡片 (Grid)」或工程師專用「緊湊清單表格 (Table)」。
3. **既有與未來報告無縫跳轉**：
   - 卡片直連已發佈之 GitHub Pages 互動決策平台（如 [台中大安龜殼段 POCS 水上光電報告](https://davidyeh51.github.io/daan-guike-pocs-diagnostic/#summary)）。
   - 側邊抽屜 (Slide-over Drawer) 提供 5W2H、D4 根因排除假設、現場 Mini 地圖及相片證據庫快速檢視。
4. **Supabase 雲端整合 (文字與相片拖拉直傳)**：
   - 整合 Supabase PostgreSQL 資料表 (`plants`, `reports_8d`, `report_evidences`)。
   - 現場巡檢照片、施工圖紙、SCADA 截圖與熱像圖直接拖拉上傳至 Supabase Storage `solar-8d-evidences` 存儲空間，自動生成公開 URL 並入庫。
   - 具備連線狀態指示燈與「本地展示模式 (LocalStorage Fallback)」，無網路或尚未配置金鑰時仍可完整操作與體驗。
5. **標準規範輸出相容性**：
   - 支援一鍵匯出符合 `generate_solar_platform.py` 標準的 `plant_spec.json`。
   - 支援一鍵匯出全庫 CSV 對帳檔（內建 UTF-8 BOM，可直接用 Excel 開啟）。

---

## 🚀 快速開始 (Quick Start)

### 方式 A：直接本機開啟入口網頁
1. 直接使用 Chrome / Edge 瀏覽器開啟專案目錄下的 [`index.html`](./index.html)。
2. 預設即以「本地展示模式」載入包含「台中大安龜殼段 POCS 水上光電」等 4 個典型案場數據。
3. 點擊任意卡片的「開啟互動診斷報告」，即可跳轉至線上展示報告。

---

### 方式 B：串接 Supabase 雲端資料庫與相片存儲桶

若要將資料持久化至雲端並供團隊多人即時協作上傳相片：

#### 步驟 1：在 Supabase 建立專案
1. 前往 [Supabase 官網 (supabase.com)](https://supabase.com/) 登入並建立新專案。

#### 步驟 2：執行資料庫與儲存桶配置腳本
1. 進入 Supabase 控制台左側選單的 **SQL Editor**。
2. 開啟本專案的 [`supabase/schema.sql`](./supabase/schema.sql) 檔案，將完整內容貼入 SQL Editor。
3. 點擊 **Run** 執行：
   - 自動建立 `plants`, `reports_8d`, `report_evidences` 三張資料表與索引。
   - 自動建立 `solar-8d-evidences` 公開相片儲存空間 (Storage Bucket)。
   - 自動設定公開讀取 (Public Read) 與免登入直傳 (Anon Insert) 之安全存取策略 (RLS)。
   - 自動植入大安龜殼段等示範資料。

#### 步驟 3：在入口網頁填入連線金鑰
1. 在 Supabase 控制台點擊 **Project Settings** $\rightarrow$ **API**。
2. 複製 **Project URL** 與 **Project API Keys (anon public)**。
3. 打開 [`index.html`](./index.html)，點擊右上角的 **「⚙️ Supabase 設定」**。
4. 貼上 URL 與 Anon Key，點擊 **「測試連線」**。確認顯示「✅ 連線成功」後點擊 **「儲存並連線」**。
5. 頂部狀態燈號隨即切換為 **「🟢 Supabase 雲端已連線」**。

---

## 📸 如何新增報告與上傳現場照片？

1. 點擊頂部右上角 **「+ 新增 8D 報告」** 按鈕。
2. **分頁 1（案場參數）**：輸入案號（如 `PV-2026-CS05`）、電廠全名、容量 kWp、坐標與嚴重等級。
3. **分頁 2（8D 分析）**：填寫核心一句話（The Lede）、管理缺口（Takeaway）、異常機台與損失度數。
4. **分頁 3（相片直傳）**：
   - 將現場巡檢實拍、熱像儀 (IR) 圖片或空拍圖直接**拖拉進藍色虛線框**。
   - 系統自動編號為 `EV-01`, `EV-02`... 並直傳至 Supabase Storage，即時顯示縮圖。
5. **分頁 4（交付網址）**：若此案場已有編譯好的 GitHub Pages 報告，貼入網址；亦可點擊「匯出相容 plant_spec.json」。
6. 點擊 **「儲存報告資料」**，系統將即時寫入資料庫並同步更新門戶戰情看板！

---

## 🛠️ 與既有 Python 報告生成器整合

當您在門戶中填寫完案場資料並匯出 `PV-xxxx_spec.json` 後，可隨時使用內建腳本編譯出標準的獨立 HTML 決策平台：

```bash
# 位於專案目錄下執行
python skills/solar-8d-diagnostic/scripts/generate_solar_platform.py \
  --spec PV-2026-DA01_spec.json \
  --output 大安龜殼段POCS_診斷報告.html
```

隨後推播至 GitHub 儲存庫的 `gh-pages` 或 `main` 分支，即可透過 GitHub Pages 取得公開網址並回填至管理門戶。

---

## 📁 檔案結構

```
8.4 維運服務/
├── index.html                   # 8D 診斷報告管理入口門戶 (單一檔案可攜、即開即用)
├── 大安龜殼段POCS_診斷報告.html    # 典範 8D 決策平台單一獨立報告 (HTML)
├── README_PORTAL.md             # 本操作與架構指引文件
├── supabase/
│   └── schema.sql               # Supabase PostgreSQL 建表、RLS、Storage 與種子資料腳本
└── skills/
    └── solar-8d-diagnostic/     # 8D 光電異常排查暨平台生成 Skill
        ├── SKILL.md
        ├── references/          # 8D 方法論與 HTML 視覺架構規範
        ├── resources/           # Markdown 報告範本與檢驗清單
        ├── examples/            # 大安龜殼段完整示範 spec.json
        └── scripts/             # generate_solar_platform.py 自動編譯引擎
```
