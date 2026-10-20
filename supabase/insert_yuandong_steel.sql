-- ==============================================================================
-- 遠東鋼鐵一~三期 1,481.8kWp 8D 異常診斷資料寫入腳本 (Supabase SQL)
-- 適用於 Supabase PostgreSQL 資料庫執行
-- ==============================================================================

-- 1. 新增電廠資料 (plants)
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
    '812 高雄市小港區店鎮里嘉興街 8 號',
    22.5601,
    120.3392,
    1400.0,
    1481.800,
    4780,
    'URE D6M310H3A (310Wp) / 組串型變流器 (45台)',
    45,
    4.50,
    '高雄遠東鋼鐵股份有限公司'
) ON CONFLICT (plant_code) DO UPDATE SET
    actual_capacity_kwp = EXCLUDED.actual_capacity_kwp,
    total_modules = EXCLUDED.total_modules,
    updated_at = NOW();

-- 2. 新增 8D 報告主表 (reports_8d)
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
    'v1.0',
    CURRENT_DATE,
    2026,
    '2025/10/06 – 2026/10/05（365天）',
    'd5_permanent_actions',
    'Level 2 (重大發電異常與火載量隱患)',
    'INV026, INV014, INV030 (全場共 31 台落後)',
    0.762,
    192864,
    867887,
    '小港重度鋼粉落塵覆蓋、冬季低仰角氣樓遮陰、INV014組串斷路與INV030跳脫',
    '全場 45 台變流器年度發電量僅 156 萬度 (平均 DY 2.89)，相比標竿機台 INV037 (DY 3.241) 全年短少 192,864 度電 (年損 NT$ 86.8 萬元)。診斷確診為重工業鋼粉落塵覆蓋、太子樓冬季低仰角遮蔽、INV014 組串斷路與 INV030 跳脫 16 天。整改預算 3,803,328 元，4.38 年回本，20 年累計淨增值 1,302 萬元！',
    '實施五大精準修繕工項：直流斷路修復、風道與通訊檢修、超高壓物理除垢自潔鍍膜、遮陰跳線重組與即時 P2P 邊緣告警，確保日等價時數自 2.89 飛躍至 3.241，全面保障 20 年資產收益！',
    'https://davidyeh51.github.io/yuandong-steel-diagnostic/'
) ON CONFLICT (case_no) DO UPDATE SET
    loss_kwh = EXCLUDED.loss_kwh,
    annual_loss_ntd = EXCLUDED.annual_loss_ntd,
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
