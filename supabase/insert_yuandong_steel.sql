-- ==============================================================================
-- 遠東鋼鐵一~三期 1,481.8kWp 8D 異常診斷資料寫入腳本 (Supabase SQL)
-- 適用於 Supabase PostgreSQL 資料庫執行（2026/10/30 核定更新版）
-- ==============================================================================

-- 1. 新增/更新電廠資料 (plants)
INSERT INTO public.plants (
    plant_code,
    name,
    plant_type,
    location,
    lat,
    lng,
    contract_kw,
    actual_capacity_kwp,
    total_modules,
    inverter_model,
    inverter_count,
    fit_rate,
    owner_name
) VALUES (
    'KH01',
    '遠東鋼鐵一~三期屋頂型光電電廠',
    '屋頂型',
    '812 高雄市小港區店鎮里嘉興街 8 號（北林路口）',
    22.561446,
    120.365215,
    1400.0,
    1481.800,
    4780,
    'DELTA RPI-M30A (45台，30kW 雙MPPT) / URE D6M310H3A (310Wp 4,780片)',
    45,
    5.15,
    '高雄遠東鋼鐵股份有限公司'
) ON CONFLICT (plant_code) DO UPDATE SET
    location = EXCLUDED.location,
    lat = EXCLUDED.lat,
    lng = EXCLUDED.lng,
    actual_capacity_kwp = EXCLUDED.actual_capacity_kwp,
    total_modules = EXCLUDED.total_modules,
    inverter_model = EXCLUDED.inverter_model,
    fit_rate = EXCLUDED.fit_rate,
    updated_at = NOW();

-- 2. 新增/更新 8D 報告主表 (reports_8d)
WITH target_plant AS (
    SELECT id FROM public.plants WHERE plant_code = 'KH01' LIMIT 1
)
INSERT INTO public.reports_8d (
    plant_id,
    case_no,
    report_title,
    report_version,
    publish_date,
    year,
    data_period,
    stage,
    severity_level,
    abnormal_device,
    ratio_to_benchmark,
    loss_kwh,
    annual_loss_ntd,
    priority_issue,
    lede,
    takeaway,
    report_url
) VALUES (
    (SELECT id FROM target_plant),
    'PV-2026-KH01',
    '高雄小港遠東鋼鐵一~三期 1,481.8kWp｜8D 性能異常診斷暨效益改善決策報告',
    'v1.1 (2026/10/30 核定更新版)',
    CURRENT_DATE,
    2026,
    '2025/10/06 – 2026/10/05（365天，併聯日 2019/04/13）',
    'd5_permanent_actions',
    'Level 2 (重大發電異常與火載量隱患)',
    'INV026, INV014, INV030 (全場共 31 台落後)',
    0.762,
    192864,
    993247,
    '小港鋼粉重度落塵覆蓋、冬季低仰角氣樓遮陰、INV014雙MPPT單串斷路與INV030跳脫',
    '全場 45 台 DELTA RPI-M30A 年度發電量僅 156 萬度 (平均 DY 2.89)，相比標竿機台 INV037 (DY 3.241) 全年短少 192,864 度電 (年損電費 NT$ 99.3 萬元，以綠電 5.15 元/度計)。診斷確診為重工業鋼粉落塵覆蓋、太子樓冬季低仰角遮蔽、INV014 雙MPPT單串斷路與 INV030 跳脫 16 天。整改預算 3,803,328 元，3.83 年回本，合約剩餘 12.5 年累計回補 1,241.6 萬元，扣除整改成本淨增值高達 861.2 萬元！',
    '實施五大精準修繕工項：DELTA M30A 直流斷路修復、風道與通訊檢修、超高壓物理除垢自潔鍍膜、遮陰跳線重組與即時 P2P 邊緣告警，確保日等價時數自 2.89 飛躍至 3.241，全面保障 12.5 年合約收益！',
    'https://davidyeh51.github.io/yuandong-steel-diagnostic/'
) ON CONFLICT (case_no) DO UPDATE SET
    loss_kwh = EXCLUDED.loss_kwh,
    annual_loss_ntd = EXCLUDED.annual_loss_ntd,
    lede = EXCLUDED.lede,
    takeaway = EXCLUDED.takeaway,
    report_url = EXCLUDED.report_url,
    updated_at = NOW();

-- 3. 新增工單資料表支援 (work_orders)
CREATE TABLE IF NOT EXISTS public.work_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_no VARCHAR(64) NOT NULL,
    plant_name VARCHAR(255) NOT NULL,
    signer_name VARCHAR(128) NOT NULL,
    signer_contact VARCHAR(128) NOT NULL,
    budget_ntd NUMERIC(12, 2) DEFAULT 3803328.00,
    fit_rate NUMERIC(6, 2) DEFAULT 5.15,
    schedule_notes TEXT,
    notes TEXT,
    status VARCHAR(32) DEFAULT 'pending_approval',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.work_orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "允許公開訪客或客戶在線提交整改工單"
    ON public.work_orders FOR INSERT
    WITH CHECK (true);

CREATE POLICY "允許已認證維運人員讀取工單"
    ON public.work_orders FOR SELECT
    USING (true);
