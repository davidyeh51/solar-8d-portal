-- ==============================================================================
-- 彰化鹿港彰濱・易昇塑膠 1,771.2 kWp 8D 異常診斷與三角色資料寫入腳本 (Supabase SQL)
-- 對應 OSS 案號：12309021 / SCADA：CH-YS-001 / 8D 案號：PV-2026-YSP01
-- 產出日期：2026/11/12
-- ==============================================================================

-- 1. 新增/更新電廠基本資料 (plants)
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
    'CH-YS-001',
    '彰化鹿港彰濱・易昇塑膠地面型光電電廠',
    '地面型',
    '505 彰化縣鹿港鎮上林段 531-2 地號（鹿工南六路18號・彰濱工業區）',
    24.067161,
    120.386488,
    1500.00,
    1771.200,
    4320,
    'Prime VOLT PV-125KH-U × 12台 (125kW) / URE DBK410HFA-410 × 4,320片 (24串15併)',
    12,
    4.1657,
    '易昇塑膠股份有限公司'
) ON CONFLICT (plant_code) DO UPDATE SET
    name = EXCLUDED.name,
    plant_type = EXCLUDED.plant_type,
    location = EXCLUDED.location,
    lat = EXCLUDED.lat,
    lng = EXCLUDED.lng,
    contract_kw = EXCLUDED.contract_kw,
    actual_capacity_kwp = EXCLUDED.actual_capacity_kwp,
    total_modules = EXCLUDED.total_modules,
    inverter_model = EXCLUDED.inverter_model,
    inverter_count = EXCLUDED.inverter_count,
    fit_rate = EXCLUDED.fit_rate,
    owner_name = EXCLUDED.owner_name,
    updated_at = NOW();

-- 2. 新增/更新 8D 報告主表 (reports_8d)
WITH target_plant AS (
    SELECT id FROM public.plants WHERE plant_code = 'CH-YS-001' LIMIT 1
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
    report_url,
    spec_json
) VALUES (
    (SELECT id FROM target_plant),
    'PV-2026-YSP01',
    '彰化鹿港易昇塑膠 1,771.2kWp｜UNSW 性能診斷暨 8D 三角色決策報告',
    'v1.0 (2026/11/12 診斷發布)',
    '2026-11-12',
    2026,
    '2026/08/12 – 2026/11/11（92 天 / 26,496 筆 5 分鐘遙測）',
    'd4_root_cause',
    'Level 2 (11/09 突發 -6.49% 驟降＋濱海落塵＋假數據審計)',
    '全廠彙總 DC/INV (11/09 13:25 驟降-6.49%)｜SCADA夜間假發電｜22.8kV MOF防蝕',
    0.922,
    58945.70,
    1033280.00,
    '11/09 13:25 突發 -6.49% PR / -6.68% I/G 階梯驟降（約1台INV或11~12串離線），疊加 6° 低傾角濱海落塵年損 NT$ 40.7 萬，且 alarm_site_cases 零告警與 SCADA 夜間假正發電 +157.5 kWh/日。',
    '92 天潔淨發電 647,208.1 kWh，10/01 後電表 291,004.0 kWh 與潔淨變流器 291,331.7 kWh 僅差 0.11%，證實核心硬體健全（晴空基準 PR 84.69%、效率 98.91%）；但 11/09 13:25 突發 -6.49% 階梯失落相當於 1/12 容量靜默掉線（年化風險 NT$ 59.9 萬），疊加 6° 濱海落塵（年損 NT$ 40.7 萬），整體未處置年化風險達 248,045 度（NT$ 103.3 萬）。僅投入 NT$ 5 萬整改與條件式清洗，17 年 NPV@5% 達 NT$ 809.8 萬~873.8 萬，回收期 0.8 個月！',
    '監控不是沒壞，是全廠匯流總表與 10/01 夜間 +13kW 假發電掩蓋了驟降！合約 clean_cycle = 0 且 hv_by_us = 否，須立即明確三角色權責並補齊 INV-01~12 分機實測推進至 D6-D8 閉環。',
    'https://davidyeh51.github.io/yisheng-plastic-diagnostic/',
    jsonb_build_object(
        'oss_field_no', '12309021',
        'scada_code', 'CH-YS-001',
        'tariff_ntd', 4.1657,
        'audit_rubric_100', 89.0,
        'trace_score_50', 44
    )
) ON CONFLICT (case_no) DO UPDATE SET
    plant_id = EXCLUDED.plant_id,
    report_title = EXCLUDED.report_title,
    stage = EXCLUDED.stage,
    severity_level = EXCLUDED.severity_level,
    abnormal_device = EXCLUDED.abnormal_device,
    ratio_to_benchmark = EXCLUDED.ratio_to_benchmark,
    loss_kwh = EXCLUDED.loss_kwh,
    annual_loss_ntd = EXCLUDED.annual_loss_ntd,
    priority_issue = EXCLUDED.priority_issue,
    lede = EXCLUDED.lede,
    takeaway = EXCLUDED.takeaway,
    report_url = EXCLUDED.report_url,
    spec_json = EXCLUDED.spec_json,
    updated_at = NOW();

-- 3. 寫入 8D 證據資料庫 (report_evidences)
WITH target_report AS (
    SELECT id FROM public.reports_8d WHERE case_no = 'PV-2026-YSP01' LIMIT 1
)
INSERT INTO public.report_evidences (
    report_id, ev_code, category, title, description, step_tag, image_url, storage_path, taken_at, uploader
) VALUES
(
    (SELECT id FROM target_report), 'EV-01', 'SCADA 審計證據', '10/01 SCADA 重映射致 +152,416 kWh 跳變與夜間 +13kW 假發電',
    '10/01 00:00 inv_kwh_cum 跳升 +152,416 kWh 並伴隨夜間恆定 +13kW 假正輸出；剔除後 42 天潔淨 AC (291,331.7 kWh) 與電表 (291,004.0 kWh) 僅差 0.11%。',
    'D2', 'https://davidyeh51.github.io/yisheng-plastic-diagnostic/#slide-4', 'audit/ev01_scada_remap.json', '2026/11/12', 'AI 診斷團隊'
),
(
    (SELECT id FROM target_report), 'EV-02', '電氣時序異常', '11/09 13:25 突發 -6.49% PR 與 -6.68% I/G 階梯驟降',
    '11/11 PR 69.87% 較 11/08 74.18%（相對跌幅 -6.49%），I/G 下跌 -6.68%，但 Vdc 維持 ~701V、效率維持 98.91%，符合並聯組串斷路或單台 INV 離線（約 1/12 容量）。',
    'D4', 'https://davidyeh51.github.io/yisheng-plastic-diagnostic/#slide-5', 'telemetry/ev02_step_drop.json', '2026/11/11', 'AI 診斷團隊'
),
(
    (SELECT id FROM target_report), 'EV-03', '物理模擬驗證', 'pvlib 晴空反演最佳擬合 (tilt=6°, azim=180°, RMSE 21.7 W/m²)',
    '54 組傾角/方位角窮舉驗證竣工圖 6° 正南鋪設，上午比 0.990、下午比 1.015；15:00-16:30 受 WSW 微遮陰 PR 降至 55.4%（年損僅 NT$ 2.75 萬）。',
    'D4', 'https://davidyeh51.github.io/yisheng-plastic-diagnostic/#slide-6', 'pvlib/ev03_clearsky_fit.json', '2026/11/12', 'AI 診斷團隊'
),
(
    (SELECT id FROM target_report), 'EV-04', '光學積塵實證', '6° 低傾角濱海積塵：10/22-25 降雨回升 +4.81 pp 後再度衰減 -5.84 pp',
    '10/21 晴空 PR 75.85% 經降雨自然沖刷跳升至 10/26 80.66%，隨後 13 個乾燥日跌回 11/08 74.18%，年化清洗不作為損失達 NT$ 40.7 萬（合約 clean_cycle = 0）。',
    'D4', 'https://davidyeh51.github.io/yisheng-plastic-diagnostic/#slide-7', 'soiling/ev04_rain_recovery.json', '2026/11/08', 'AI 診斷團隊'
),
(
    (SELECT id FROM target_report), 'EV-05', '施工圖紙', '台電審訖圖 E-3 紅印提醒 MOF 及電表箱防鏽蝕與 08/22-26 停機紀錄',
    '08/22 17:25~08/26 15:55 全站停止累積損失 28,171.7 度（NT$ 11.7 萬）；OSS hv_by_us=否且 E-3 台電紅印載明 113.3.06 要求 MOF/電表箱防蝕維護。',
    'D3', 'https://davidyeh51.github.io/yisheng-plastic-diagnostic/#slide-8', 'drawings/ev05_taipower_e3.pdf', '2024/03/06', '台電彰化區處 / OSS'
),
(
    (SELECT id FROM target_report), 'EV-06', '財務分析報表', '17 年剩餘躉購期 DCF 淨現值 NT$ 809.8 萬~873.8 萬（回收期 0.8 個月）',
    '一次性整改 NT$ 50,000 + 年清洗 OPEX NT$ 144,000（ROI 103.6%），首年淨回收 NT$ 747,764，17 年 NPV@5% 達 NT$ 8,098,474（含防停機 NT$ 8,737,895）。',
    'D5', 'https://davidyeh51.github.io/yisheng-plastic-diagnostic/#slide-9', 'finance/ev06_17yr_dcf.json', '2026/11/12', 'AI 診斷團隊'
) ON CONFLICT (report_id, ev_code) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    image_url = EXCLUDED.image_url;

-- 4. 寫入現場工單 (work_orders)
INSERT INTO public.work_orders (
    case_no, plant_name, signer_name, signer_contact, budget_ntd, fit_rate, schedule_notes, notes, status
) VALUES (
    'PV-2026-YSP01',
    '彰化鹿港彰濱・易昇塑膠 (1,771.2kWp)',
    '羅健國 (Jingkuo)｜待分機檢修派工',
    'OSS #12309021 / 中區維運組',
    50000.00,
    4.1657,
    '優先項目：11/09 -6.49% 階梯失落之 INV-01~12 DC 鉗流檢修 + SCADA 夜間假發電修補',
    'Stage-1 必檢：(1) LOTO 後量測 INV-01~12 各 15 串(#1-13,#15,#17) DC電流；(2) 調閱 11/09 13:25 變流器故障碼；(3) 查核 22.8kV MOF/電表箱蝕鏽(業主負責高保)；(4) 15:00-16:30 複查 WSW 遮陰。',
    'pending_inspection'
) ON CONFLICT (case_no, signer_name) DO UPDATE SET
    budget_ntd = EXCLUDED.budget_ntd,
    schedule_notes = EXCLUDED.schedule_notes,
    notes = EXCLUDED.notes,
    status = EXCLUDED.status;
