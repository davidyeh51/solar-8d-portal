-- ==============================================================================
-- 太陽光電電廠 8D 異常診斷決策管理門戶 (Solar 8D Diagnostic Hub)
-- Supabase PostgreSQL 資料庫結構與 Storage 權限配置腳本
-- ==============================================================================

-- 啟用 UUID 擴充功能
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 1. 電廠基本資料表 (plants)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.plants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plant_code VARCHAR(64) UNIQUE NOT NULL,      -- 例如: DA01, ZB02, TX03
    name VARCHAR(255) NOT NULL,                  -- 例如: 台中市大安區龜殼段 POCS 水上光電
    plant_type VARCHAR(64) DEFAULT '水上浮體型',  -- 水上浮體型 / 地面型 / 屋頂型 / 漁電共生
    location TEXT NOT NULL,                      -- 詳細地址或地號
    lat NUMERIC(10, 6),                          -- 緯度 (例如: 24.3800)
    lng NUMERIC(10, 6),                          -- 經度 (例如: 120.5750)
    contract_kw NUMERIC(10, 2) DEFAULT 0,        -- 簽約容量 (kW)
    actual_capacity_kwp NUMERIC(10, 3) NOT NULL, -- 竣工實際容量 (kWp)
    total_modules INTEGER DEFAULT 0,             -- 組件片數
    inverter_model VARCHAR(128),                 -- 逆變器型號 (例如: SUNGROW SG110CX)
    inverter_count INTEGER DEFAULT 1,            -- 逆變器台數
    fit_rate NUMERIC(6, 2) DEFAULT 5.00,         -- 躉購費率 (NT$/kWh)
    owner_name VARCHAR(128),                     -- 業主或資產擁有人 (例如: 匯僑)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 2. 8D 診斷報告主表 (reports_8d) - 支援每年 100+ 份報告
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.reports_8d (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plant_id UUID REFERENCES public.plants(id) ON DELETE CASCADE,
    case_no VARCHAR(64) UNIQUE NOT NULL,         -- 案號 (例如: PV-2026-DA01)
    report_title VARCHAR(255) NOT NULL,         -- 報告名稱 (例如: 台中市大安區龜殼段 POCS 水上光電｜INV-13 發電異常)
    report_version VARCHAR(32) DEFAULT 'v1.0',
    publish_date DATE NOT NULL DEFAULT CURRENT_DATE,
    year INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM CURRENT_DATE),
    data_period VARCHAR(128),                   -- 資料期間 (例如: 2026/06/20 – 09/17（90 天）)
    
    -- 8D 狀態與嚴重等級
    stage VARCHAR(32) NOT NULL DEFAULT 'd0_emergency', -- d0_emergency / d2_analysis / d4_root_cause / d6_verification / d8_closed
    severity_level VARCHAR(64) NOT NULL DEFAULT 'Level 2 (重大發電異常與火載量隱患)',
    
    -- 核心量化指標 (KPIs)
    abnormal_device VARCHAR(64) DEFAULT 'INV-13',-- 主要異常設備
    ratio_to_benchmark NUMERIC(5, 3),            -- 相對基準比值 (例如: 0.450 代表 45%)
    loss_kwh NUMERIC(12, 2) DEFAULT 0,           -- 短少發電度數 (kWh)
    annual_loss_ntd NUMERIC(12, 2) DEFAULT 0,    -- 年化損失金額 (NT$)
    priority_issue TEXT,                         -- 優先處置問題 (例如: INV-13 雜草覆蓋模組與草屑留置)
    
    -- 核心金句與文字結論
    lede TEXT,                                   -- 核心一句話 (The Lede)
    takeaway TEXT,                               -- 真正的管理缺口 (Takeaway)
    
    -- 交付網址 (例如 GitHub Pages 靜態站點網址)
    report_url TEXT,                             -- 例如: https://davidyeh51.github.io/daan-guike-pocs-diagnostic/#summary
    
    -- 完整規格 JSON 備份 (相容於 plant_spec.json 與 generate_solar_platform.py)
    spec_json JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 3. 8D 相片與證據資料表 (report_evidences)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.report_evidences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID REFERENCES public.reports_8d(id) ON DELETE CASCADE,
    ev_code VARCHAR(32) NOT NULL,                -- 證據編號 (例如: EV-01, EV-02, EV-03)
    category VARCHAR(64) DEFAULT '現場巡檢實拍', -- 現場巡檢實拍 / 施工圖紙 / SCADA 截圖 / 紅外線熱像 (IR)
    title VARCHAR(255) NOT NULL,                -- 標題 (例如: 2026/09/10 除草作業後現場實拍)
    description TEXT,                           -- 實證說明與推論
    step_tag VARCHAR(32) DEFAULT 'D4',           -- 對應步驟 (D0, D2, D3, D4, D5, D6, D7)
    image_url TEXT NOT NULL,                     -- Supabase Storage 公開網址或 CDN 連結
    storage_path TEXT,                           -- Storage 中的檔案路徑
    taken_at VARCHAR(64),                        -- 拍攝時間戳記 (例如: 2026/09/21 09:52)
    uploader VARCHAR(64) DEFAULT '機電維運組',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 4. 索引建立 (針對 100+ 份/年之高頻查詢加速)
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_reports_year ON public.reports_8d(year);
CREATE INDEX IF NOT EXISTS idx_reports_stage ON public.reports_8d(stage);
CREATE INDEX IF NOT EXISTS idx_reports_severity ON public.reports_8d(severity_level);
CREATE INDEX IF NOT EXISTS idx_reports_case_no ON public.reports_8d(case_no);
CREATE INDEX IF NOT EXISTS idx_plants_code ON public.plants(plant_code);
CREATE INDEX IF NOT EXISTS idx_evidences_report ON public.report_evidences(report_id);

-- ------------------------------------------------------------------------------
-- 5. 自動更新時間戳記觸發器 (updated_at Trigger)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_plants_updated_at ON public.plants;
CREATE TRIGGER set_plants_updated_at
BEFORE UPDATE ON public.plants
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS set_reports_updated_at ON public.reports_8d;
CREATE TRIGGER set_reports_updated_at
BEFORE UPDATE ON public.reports_8d
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------------------------------------
-- 6. Supabase Storage 儲存空間建立 (solar-8d-evidences)
-- ------------------------------------------------------------------------------
INSERT INTO storage.buckets (id, name, public)
VALUES ('solar-8d-evidences', 'solar-8d-evidences', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- ------------------------------------------------------------------------------
-- 7. Row Level Security (RLS) 安全策略設定
-- ------------------------------------------------------------------------------
ALTER TABLE public.plants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports_8d ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_evidences ENABLE ROW LEVEL SECURITY;

-- 允許所有人 (包含匿名 anon) 讀取公開報告資料庫
DROP POLICY IF EXISTS "Public Read Plants" ON public.plants;
CREATE POLICY "Public Read Plants" ON public.plants FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public Read Reports" ON public.reports_8d;
CREATE POLICY "Public Read Reports" ON public.reports_8d FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public Read Evidences" ON public.report_evidences;
CREATE POLICY "Public Read Evidences" ON public.report_evidences FOR SELECT USING (true);

-- 允許匿名與授權使用者寫入與更新 (以利門戶網頁免登入即可上傳維運數據)
DROP POLICY IF EXISTS "Allow Insert Plants" ON public.plants;
CREATE POLICY "Allow Insert Plants" ON public.plants FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Allow Update Plants" ON public.plants;
CREATE POLICY "Allow Update Plants" ON public.plants FOR UPDATE USING (true);

DROP POLICY IF EXISTS "Allow Delete Plants" ON public.plants;
CREATE POLICY "Allow Delete Plants" ON public.plants FOR DELETE USING (true);

DROP POLICY IF EXISTS "Allow Insert Reports" ON public.reports_8d;
CREATE POLICY "Allow Insert Reports" ON public.reports_8d FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Allow Update Reports" ON public.reports_8d;
CREATE POLICY "Allow Update Reports" ON public.reports_8d FOR UPDATE USING (true);

DROP POLICY IF EXISTS "Allow Delete Reports" ON public.reports_8d;
CREATE POLICY "Allow Delete Reports" ON public.reports_8d FOR DELETE USING (true);

DROP POLICY IF EXISTS "Allow Insert Evidences" ON public.report_evidences;
CREATE POLICY "Allow Insert Evidences" ON public.report_evidences FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Allow Update Evidences" ON public.report_evidences;
CREATE POLICY "Allow Update Evidences" ON public.report_evidences FOR UPDATE USING (true);

DROP POLICY IF EXISTS "Allow Delete Evidences" ON public.report_evidences;
CREATE POLICY "Allow Delete Evidences" ON public.report_evidences FOR DELETE USING (true);

-- Storage 物件策略 (允許公開存取與直接上傳至 solar-8d-evidences bucket)
DROP POLICY IF EXISTS "Public Access Evidences Bucket" ON storage.objects;
CREATE POLICY "Public Access Evidences Bucket" ON storage.objects
FOR SELECT USING (bucket_id = 'solar-8d-evidences');

DROP POLICY IF EXISTS "Allow Upload Evidences Bucket" ON storage.objects;
CREATE POLICY "Allow Upload Evidences Bucket" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'solar-8d-evidences');

DROP POLICY IF EXISTS "Allow Update Evidences Bucket" ON storage.objects;
CREATE POLICY "Allow Update Evidences Bucket" ON storage.objects
FOR UPDATE USING (bucket_id = 'solar-8d-evidences');

-- ------------------------------------------------------------------------------
-- 8. 示範種子數據 (含台中大安龜殼段及典型光電異常案場)
-- ------------------------------------------------------------------------------

-- 案場 1: 台中大安龜殼段 POCS 水上光電 (真實基準案例)
INSERT INTO public.plants (
    id, plant_code, name, plant_type, location, lat, lng, 
    contract_kw, actual_capacity_kwp, total_modules, inverter_model, inverter_count, fit_rate, owner_name
) VALUES (
    'a1b2c3d4-e5f6-4a5b-8c9d-012345678901',
    'DA01',
    '台中市大安區龜殼段 POCS 水上光電',
    '水上浮體型',
    '台中市大安區龜殼段 253-1 地號 (溫寮溪出海口南岸 / 西濱快速道路台61線旁)',
    24.380000,
    120.575000,
    812.00,
    1505.155,
    4493,
    'SUNGROW SG110CX (110kW 級)',
    13,
    5.00,
    '匯僑'
) ON CONFLICT (plant_code) DO NOTHING;

-- 案場 2: 彰濱工業區鹿港段地面型案場
INSERT INTO public.plants (
    id, plant_code, name, plant_type, location, lat, lng, 
    contract_kw, actual_capacity_kwp, total_modules, inverter_model, inverter_count, fit_rate, owner_name
) VALUES (
    'a1b2c3d4-e5f6-4a5b-8c9d-012345678902',
    'ZB02',
    '彰濱工業區鹿港區二期地面光電廠',
    '地面型',
    '彰化縣鹿港鎮鹿工北二路 18 號周邊',
    24.062100,
    120.413200,
    1980.00,
    2450.600,
    6800,
    'HUAWEI SUN2000-100KTL',
    22,
    4.85,
    '和順能源'
) ON CONFLICT (plant_code) DO NOTHING;

-- 案場 3: 雲林台西水上型暨浮體案場
INSERT INTO public.plants (
    id, plant_code, name, plant_type, location, lat, lng, 
    contract_kw, actual_capacity_kwp, total_modules, inverter_model, inverter_count, fit_rate, owner_name
) VALUES (
    'a1b2c3d4-e5f6-4a5b-8c9d-012345678903',
    'TX03',
    '雲林台西養殖滯洪池浮體光電廠',
    '漁電共生',
    '雲林縣台西鄉海口段 1102 地號',
    23.705400,
    120.198200,
    1200.00,
    1480.000,
    4100,
    'Delta M100A (100kW 級)',
    15,
    5.12,
    '永鑫能源'
) ON CONFLICT (plant_code) DO NOTHING;

-- 案場 4: 嘉義布袋鹽灘地地面型光電案場
INSERT INTO public.plants (
    id, plant_code, name, plant_type, location, lat, lng, 
    contract_kw, actual_capacity_kwp, total_modules, inverter_model, inverter_count, fit_rate, owner_name
) VALUES (
    'a1b2c3d4-e5f6-4a5b-8c9d-012345678904',
    'BD04',
    '嘉義布袋鹽灘地綠能生態光電專區',
    '地面型',
    '嘉義縣布袋鎮鹽館段 88 號',
    23.371200,
    120.158700,
    3200.00,
    3980.400,
    10800,
    'SUNGROW SG125HX',
    32,
    4.65,
    '台灣綠能資產'
) ON CONFLICT (plant_code) DO NOTHING;

-- 8D 報告 1: 大安龜殼段 8D 診斷報告 (現有真實報告)
INSERT INTO public.reports_8d (
    id, plant_id, case_no, report_title, report_version, publish_date, year, data_period,
    stage, severity_level, abnormal_device, ratio_to_benchmark, loss_kwh, annual_loss_ntd, priority_issue,
    lede, takeaway, report_url
) VALUES (
    'b2c3d4e5-f6a7-5b6c-9d0e-123456789001',
    'a1b2c3d4-e5f6-4a5b-8c9d-012345678901',
    'PV-2026-DA01',
    '台中市大安區龜殼段 POCS 水上光電｜INV-13 發電異常',
    'v1.0',
    '2026-09-21',
    2026,
    '2026/06/20 – 09/17（90 天）',
    'd4_root_cause',
    'Level 2 (重大發電異常與火載量隱患)',
    'INV-13',
    0.450,
    24785.00,
    690000.00,
    'INV-13 雜草覆蓋模組與草屑未清運',
    '根因是雜草覆蓋模組，不是電氣故障。而且 9/10 的除草作業把割下的草留在模組上，讓 INV-13 比除草前更差。',
    '真正的管理缺口不是「沒有除草」，是「割完沒有清模組面」。前者是頻率問題，後者是驗收條件問題——而後者讓這次除草做了等於白做，甚至倒退。',
    'https://davidyeh51.github.io/daan-guike-pocs-diagnostic/#summary'
) ON CONFLICT (case_no) DO NOTHING;

-- 8D 報告 2: 彰濱二期 INV-04 遮蔽排查
INSERT INTO public.reports_8d (
    id, plant_id, case_no, report_title, report_version, publish_date, year, data_period,
    stage, severity_level, abnormal_device, ratio_to_benchmark, loss_kwh, annual_loss_ntd, priority_issue,
    lede, takeaway, report_url
) VALUES (
    'b2c3d4e5-f6a7-5b6c-9d0e-123456789002',
    'a1b2c3d4-e5f6-4a5b-8c9d-012345678902',
    'PV-2026-ZB02',
    '彰濱工業區鹿港區二期｜INV-04 組串受藤蔓覆蓋案',
    'v1.1',
    '2026-08-15',
    2026,
    '2026/05/01 – 08/10（100 天）',
    'd6_verification',
    'Level 2 (重大發電異常與火載量隱患)',
    'INV-04',
    0.680,
    18450.00,
    447000.00,
    '南側圍籬蔓藤爬生侵入第一排支架下緣遮蔽',
    '藤蔓類植被攀爬至下排組件下緣，遮蔽最低組串二極體導通造成發電落後 32%。',
    '防護網與除草阻絕帶寬度不足 1.5 米，已施作高耐候抑草蓆與邊界修剪。',
    '#'
) ON CONFLICT (case_no) DO NOTHING;

-- 8D 報告 3: 雲林台西 INV-02 旁路二極體熱斑案
INSERT INTO public.reports_8d (
    id, plant_id, case_no, report_title, report_version, publish_date, year, data_period,
    stage, severity_level, abnormal_device, ratio_to_benchmark, loss_kwh, annual_loss_ntd, priority_issue,
    lede, takeaway, report_url
) VALUES (
    'b2c3d4e5-f6a7-5b6c-9d0e-123456789003',
    'a1b2c3d4-e5f6-4a5b-8c9d-012345678903',
    'PV-2026-TX03',
    '雲林台西滯洪池浮體廠｜INV-02 接線盒高溫熱斑處置案',
    'v2.0',
    '2026-07-08',
    2026,
    '2026/04/01 – 06/30（90 天）',
    'd8_closed',
    'Level 1 (嚴重設備損壞與火載風險)',
    'INV-02',
    0.810,
    9820.00,
    251000.00,
    '組件接線盒旁路二極體擊穿短路，熱像溫差達 42°C',
    '鳥糞長期局部遮蔽誘發熱斑效應，導致二極體連續高溫過熱熔損。',
    '已更換 3 片受損組件並全面進行空拍熱像儀 IR 巡檢，比值恢復至 0.985 結案。',
    '#'
) ON CONFLICT (case_no) DO NOTHING;

-- 8D 報告 4: 嘉義布袋 INV-08 銘牌建檔誤差
INSERT INTO public.reports_8d (
    id, plant_id, case_no, report_title, report_version, publish_date, year, data_period,
    stage, severity_level, abnormal_device, ratio_to_benchmark, loss_kwh, annual_loss_ntd, priority_issue,
    lede, takeaway, report_url
) VALUES (
    'b2c3d4e5-f6a7-5b6c-9d0e-123456789004',
    'a1b2c3d4-e5f6-4a5b-8c9d-012345678904',
    'PV-2026-BD04',
    '嘉義布袋綠能生態專區｜INV-08 平台建檔容量失真校正',
    'v1.0',
    '2026-09-02',
    2026,
    '2026/06/01 – 08/31（92 天）',
    'd8_closed',
    'Level 3 (中度發電失真/通訊異常)',
    'INV-08',
    0.915,
    3120.00,
    72000.00,
    'SCADA 平台將 120kWp 誤植為 135kWp 造成虛報落後',
    '竣工串接圖與 SCADA 點位登錄不同步，純屬數據建置誤差，硬體電氣全數正常。',
    '修訂 SCADA 銘牌校核 SOP，所有新增電廠併網前需以 C-002 圖紙交叉驗算。',
    '#'
) ON CONFLICT (case_no) DO NOTHING;

-- 證據相片示範資料 (對應大安龜殼段)
INSERT INTO public.report_evidences (
    report_id, ev_code, category, title, description, step_tag, image_url, taken_at
) VALUES 
(
    'b2c3d4e5-f6a7-5b6c-9d0e-123456789001',
    'EV-01',
    'SCADA 截圖',
    '2026/09/21 09:52 監控系統即時功率對比',
    '日射 720 W/m² 時，INV-13 交流輸出僅 31.26 kW，其餘各台 62–74 kW。明確呈現異常落後。',
    'D0',
    'https://images.unsplash.com/photo-1509391365360-2e959784a276?auto=format&fit=crop&w=1200&q=80',
    '2026/09/21 09:52'
),
(
    'b2c3d4e5-f6a7-5b6c-9d0e-123456789001',
    'EV-02',
    '施工圖紙',
    '竣工圖 C-002 模組配置與串接圖',
    '核算各台真實容量。INV-001 實為 111.9 kWp、INV-013 實為 114.6 kWp，校正平台誤差。',
    'D2',
    'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=1200&q=80',
    '2026/09/18'
),
(
    'b2c3d4e5-f6a7-5b6c-9d0e-123456789001',
    'EV-03',
    '現場巡檢實拍',
    '2026/09/10 除草後模組表面草屑留置特寫',
    '現場除草人員以背負式割草機作業，草屑四射覆蓋組件下緣，且作業後未行清洗驗收。',
    'D4',
    'https://images.unsplash.com/photo-1613665813446-82a78c468a1d?auto=format&fit=crop&w=1200&q=80',
    '2026/09/10 14:30'
);
