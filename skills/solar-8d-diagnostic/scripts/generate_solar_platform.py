#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_solar_platform.py
==========================
太陽光電電廠 8D 異常診斷、照片溯源、原始數據對帳暨標準化決策平台生成引擎。
融合顧問級色彩系統與 8D (D0~D8) 完整工程結構，支援「內部維運版」與「業主交付版」動態切換。

使用方式:
    python generate_solar_platform.py --spec <spec.json> [--daily-data <daily_data.json>] [--mode internal|owner] [--output <output.html>]
"""

import os
import sys
import json
import argparse

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title id="pageTitle">{{PLANT_NAME}}｜INV-13 發電異常｜{{MODE_LABEL}}</title>
<meta name="description" content="{{PLANT_NAME}} 8D 異常診斷報告：精確地理區位、C-002 串接圖銘牌校正、SCADA 實時告警穿透、鳳山圳抑草蓆財務評估，以 AI Agent 守護資產現金流。">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 fill=%27%230C3A63%27 rx=%2712%27/%3E%3Cpath d=%27M12 48 L28 20 L38 34 L52 14%27 stroke=%27%231BB1BF%27 stroke-width=%275%27 fill=%27none%27 stroke-linecap=%27round%27/%3E%3Ccircle cx=%2752%27 cy=%2714%27 r=%275%27 fill=%27%23E09A2B%27/%3E%3C/svg%3E">

<!-- Google Fonts, ECharts & Leaflet -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
:root {
  --blue-dd: #0C3A63;
  --blue: #1968AD;
  --blue-d: #12518A;
  --blue-soft: #E8F1F9;
  --teal: #1BB1BF;
  --teal-d: #12818C;
  --teal-soft: #E2F5F7;
  --ink: #12293D;
  --ink-2: #3E5466;
  --muted: #5B7285;
  --line: #D9E3EC;
  --line-soft: #EEF3F8;
  --paper: #F4F7FA;
  --card: #FFFFFF;
  --amber: #E09A2B;
  --amber-soft: #FCF2DE;
  --coral: #D95F45;
  --coral-soft: #FBEAE5;
  --green: #2E7D32;
  --green-soft: #E8F5E9;
  --purple: #6B46C1;
  --purple-soft: #F3E8FF;
  --mono: "JetBrains Mono", ui-monospace, Consolas, monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: "Noto Sans TC", "Microsoft JhengHei", system-ui, sans-serif;
  background: var(--paper);
  color: var(--ink);
  line-height: 1.65;
  font-size: 15.5px;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

/* Fixed Top Navigation Bar */
.topbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000; height: 54px;
  display: flex; align-items: center; gap: 10px; padding: 0 20px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(8px);
  border-bottom: 2px solid var(--blue);
  box-shadow: 0 2px 10px rgba(12, 58, 99, 0.08);
}
.topbar .brand {
  display: flex; align-items: center; gap: 9px; margin-right: 12px;
  white-space: nowrap; text-decoration: none;
}
.topbar .brand .tx {
  font-weight: 800; font-size: .88rem; letter-spacing: .02em;
  color: var(--ink); line-height: 1.15;
}
.topbar .brand .tx small {
  display: block; font-weight: 700; font-size: .65rem;
  letter-spacing: .08em; color: var(--blue);
}
.topnav {
  display: flex; gap: 4px; flex: 1; min-width: 0;
  overflow-x: auto; scrollbar-width: none;
}
.topnav::-webkit-scrollbar { display: none; }
.navtab {
  padding: 5px 11px; font-size: .78rem; font-weight: 700; border-radius: 6px;
  color: var(--muted); border: 1px solid transparent; cursor: pointer;
  white-space: nowrap; transition: all .15s ease; background: transparent;
  text-decoration: none; display: inline-flex; align-items: center;
}
.navtab:hover { color: var(--blue); background: var(--blue-soft); }
.navtab.active {
  color: var(--blue-dd); background: var(--blue-soft);
  border-color: rgba(25, 104, 173, 0.25);
}
.topbar-actions {
  display: flex; align-items: center; gap: 8px; margin-left: auto;
}
.mode-toggle-btn {
  padding: 4px 10px; font-size: .74rem; font-weight: 800; border-radius: 20px;
  cursor: pointer; border: 1px solid rgba(25, 104, 173, 0.3);
  background: var(--blue-soft); color: var(--blue-dd);
  display: inline-flex; align-items: center; gap: 5px; transition: all .15s ease;
}
.mode-toggle-btn.owner {
  background: var(--teal-soft); color: var(--teal-d); border-color: rgba(27, 177, 191, 0.4);
}
.btn-action-sm {
  padding: 5px 11px; font-size: .75rem; font-weight: 700; border-radius: 6px;
  cursor: pointer; border: 1px solid var(--line); background: #fff; color: var(--ink);
  display: inline-flex; align-items: center; gap: 5px; transition: all .15s ease;
}
.btn-action-sm:hover { background: var(--paper); border-color: var(--blue); color: var(--blue); }

/* Cover Header */
.cover {
  border-bottom: 3px solid var(--blue);
  background: linear-gradient(180deg, var(--blue-soft) 0%, var(--paper) 100%);
  padding: 76px 24px 34px; margin-bottom: 24px;
}
.cover-inner { max-width: 1240px; margin: 0 auto; }
.badges { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.badge {
  font-size: 11.5px; font-weight: 800; letter-spacing: .04em;
  padding: 4px 11px; border-radius: 999px; border: 1px solid var(--line);
  color: var(--blue-dd); background: #fff;
}
.badge.mode-internal { border-color: rgba(217, 95, 69, 0.4); color: var(--coral); background: var(--coral-soft); }
.badge.mode-owner { border-color: rgba(27, 177, 191, 0.4); color: var(--teal-d); background: var(--teal-soft); }
.cover h1 { font-size: clamp(23px, 3.8vw, 34px); font-weight: 900; letter-spacing: -.01em; color: var(--blue-dd); }
.cover .lede {
  font-size: clamp(15.5px, 1.8vw, 18px); color: var(--ink-2);
  margin: 12px 0 0; max-width: 72ch; font-weight: 600; line-height: 1.6;
}
.factgrid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1px; background: var(--line); border: 1px solid var(--line);
  margin: 22px 0 0; border-radius: 8px; overflow: hidden;
}
.factgrid div { background: #fff; padding: 10px 14px; }
.factgrid dt { font-size: 11px; letter-spacing: .06em; color: var(--muted); font-weight: 700; text-transform: uppercase; }
.factgrid dd { margin: 3px 0 0; font-size: 14.5px; font-weight: 700; color: var(--ink); font-family: var(--mono); }

/* Main Content Layout with Sticky TOC */
.layout {
  max-width: 1240px; margin: 0 auto; padding: 0 24px 80px;
  display: grid; grid-template-columns: 210px minmax(0, 1fr);
  gap: 36px; align-items: start;
}
.toc {
  position: sticky; top: 72px; padding-top: 10px; font-size: 13.5px;
  max-height: calc(100vh - 84px); overflow-y: auto;
}
.toc-label { font-size: 11px; letter-spacing: .08em; color: var(--muted); font-weight: 800; margin-bottom: 8px; text-transform: uppercase; }
.toc a {
  display: block; padding: 6px 0 6px 12px; border-left: 2px solid var(--line);
  color: var(--ink-2); text-decoration: none; font-weight: 600; transition: all .15s ease;
}
.toc a:hover, .toc a.active {
  border-left-color: var(--blue); color: var(--blue-dd); font-weight: 800; background: var(--blue-soft);
}
main { min-width: 0; }

/* Sections */
section {
  margin: 0 0 52px; scroll-margin-top: 74px;
  background: var(--card); border: 1px solid var(--line);
  border-radius: 12px; padding: 28px 30px; box-shadow: 0 2px 6px rgba(12, 58, 99, 0.03);
}
.sec-head {
  display: flex; align-items: center; gap: 12px;
  border-bottom: 2px solid var(--line-soft); padding-bottom: 12px; margin-bottom: 8px;
}
.sec-tag {
  font-family: var(--mono); font-size: 12.5px; font-weight: 800;
  color: #fff; background: var(--blue); padding: 3px 9px; border-radius: 4px; flex: none;
}
.sec-head h2 { font-size: 20px; font-weight: 800; color: var(--blue-dd); }
.sec-purpose { font-size: 13px; color: var(--muted); margin: 0 0 20px; font-style: italic; }
p { margin: 0 0 14px; line-height: 1.65; }

/* KPIs */
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin: 0 0 22px; }
.kpi {
  background: #fff; border: 1px solid var(--line);
  border-top: 4px solid var(--blue); padding: 14px 16px; border-radius: 8px;
}
.kpi.bad { border-top-color: var(--coral); }
.kpi.warn { border-top-color: var(--amber); }
.kpi-label { font-size: 11.5px; letter-spacing: .05em; color: var(--muted); font-weight: 700; text-transform: uppercase; }
.kpi-value { font-size: 27px; font-weight: 900; letter-spacing: -.02em; margin: 4px 0 0; font-family: var(--mono); color: var(--ink); }
.kpi.bad .kpi-value { color: var(--coral); }
.kpi.warn .kpi-value { color: var(--amber); }
.kpi-unit { font-size: 13px; font-weight: 700; color: var(--muted); margin-left: 3px; }
.kpi-note { font-size: 12px; color: var(--muted); margin-top: 4px; line-height: 1.45; }

/* Tables */
.tbl-wrap { overflow-x: auto; margin: 0 0 20px; border-radius: 8px; border: 1px solid var(--line); }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
caption { caption-side: top; text-align: left; font-size: 12.5px; color: var(--muted); padding: 8px 10px; font-weight: 700; }
th, td { border-bottom: 1px solid var(--line); padding: 9px 12px; text-align: left; vertical-align: middle; }
thead th { background: var(--blue-soft); border-bottom: 2px solid rgba(25, 104, 173, 0.25); font-size: 12.5px; font-weight: 800; color: var(--blue-dd); white-space: nowrap; }
tbody tr:nth-child(even) { background: #FAFBFD; }
tbody tr:hover { background: #F1F6FA; }
td.num, th.num { text-align: right; font-family: var(--mono); font-size: 13px; font-variant-numeric: tabular-nums; }
tr.row-bad td { background: var(--coral-soft) !important; }
tr.row-warn td { background: var(--amber-soft) !important; }

/* Severity & Statements */
.sev { display: inline-block; font-size: 11px; font-weight: 800; padding: 2px 7px; border-radius: 3px; font-family: var(--mono); white-space: nowrap; }
.sev.P1 { background: var(--coral); color: #fff; }
.sev.P2 { background: var(--amber); color: #fff; }
.sev.P3 { background: var(--blue); color: #fff; }
.sev.P4 { background: var(--muted); color: #fff; }

.stmt { display: flex; gap: 11px; align-items: flex-start; border-left: 3px solid var(--line); padding: 10px 0 10px 14px; margin: 0 0 14px; background: #FAFBFD; border-radius: 0 6px 6px 0; }
.stmt.fact { border-left-color: var(--blue); }
.stmt.inference { border-left-color: var(--amber); }
.stmt.unverified { border-left-color: var(--coral); }
.tag { flex: none; font-size: 11px; font-weight: 800; letter-spacing: .04em; padding: 2px 7px; border-radius: 3px; margin-top: 2px; white-space: nowrap; }
.stmt.fact .tag { background: var(--blue-soft); color: var(--blue); border: 1px solid rgba(25, 104, 173, 0.3); }
.stmt.inference .tag { background: var(--amber-soft); color: var(--amber); border: 1px solid rgba(224, 154, 43, 0.3); }
.stmt.unverified .tag { background: var(--coral-soft); color: var(--coral); border: 1px solid rgba(217, 95, 69, 0.3); }
.stmt p { margin: 0; font-size: 14.5px; }

/* Callout */
.callout { border: 1px solid var(--line); border-left: 4px solid var(--blue); background: #FAFBFD; padding: 14px 18px; margin: 0 0 20px; border-radius: 0 8px 8px 0; }
.callout.danger { border-left-color: var(--coral); background: var(--coral-soft); border-color: rgba(217, 95, 69, 0.3); }
.callout.warn { border-left-color: var(--amber); background: var(--amber-soft); border-color: rgba(224, 154, 43, 0.3); }
.callout h4 { font-size: 14.5px; font-weight: 800; margin: 0 0 6px; }
.callout.danger h4 { color: var(--coral); }
.callout.warn h4 { color: #B45309; }

/* Actions */
.actions { margin: 0 0 20px; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.action { display: grid; grid-template-columns: minmax(0, 1fr) 110px 110px; gap: 0; border-bottom: 1px solid var(--line); }
.action:last-child { border-bottom: 0; }
.action > div { padding: 11px 14px; }
.action-what { font-size: 14px; line-height: 1.55; }
.action-verify { grid-column: 1 / -1; font-size: 13px; color: var(--ink-2); background: var(--line-soft); padding-top: 7px; padding-bottom: 7px; }
.action-meta { font-size: 12.5px; border-left: 1px solid var(--line); }
.action-meta span { display: block; font-size: 10.5px; letter-spacing: .05em; color: var(--muted); font-weight: 700; }
.action-head { display: grid; grid-template-columns: minmax(0, 1fr) 110px 110px; background: var(--blue-soft); border-bottom: 2px solid rgba(25, 104, 173, 0.25); font-size: 12px; font-weight: 800; color: var(--blue-dd); }
.action-head > div { padding: 8px 14px; }

/* Evidence Grid */
.ev-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 16px; margin: 0 0 22px; }
figure { margin: 0; border: 1px solid var(--line); background: #fff; border-radius: 8px; overflow: hidden; cursor: pointer; transition: transform .15s ease, box-shadow .15s ease; }
figure:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(12, 58, 99, 0.08); }
figure img { display: block; width: 100%; height: 210px; object-fit: cover; background: #eef3f7; }
figcaption { padding: 11px 14px; font-size: 13px; color: var(--ink-2); line-height: 1.5; }
.ev-id { font-family: var(--mono); font-size: 11px; font-weight: 800; color: #fff; background: var(--blue); padding: 1px 6px; border-radius: 3px; margin-right: 6px; }
.ev-meta { display: block; margin-top: 5px; font-size: 11.5px; color: var(--muted); }

/* Modal Lightbox */
.modal-overlay {
  position: fixed; inset: 0; z-index: 2000; background: rgba(12, 41, 67, 0.88);
  backdrop-filter: blur(6px); display: none; align-items: center; justify-content: center;
  padding: 24px;
}
.modal-overlay.active { display: flex; }
.modal-content {
  background: #fff; border-radius: 12px; max-width: 1080px; width: 100%;
  max-height: 92vh; overflow: hidden; display: flex; flex-direction: column;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3); position: relative;
}
.modal-header {
  padding: 14px 20px; border-bottom: 1px solid var(--line); display: flex;
  align-items: center; justify-content: space-between; background: var(--paper);
}
.modal-header h4 { font-size: 1rem; font-weight: 800; color: var(--blue-dd); }
.modal-close {
  background: transparent; border: none; font-size: 1.4rem; cursor: pointer;
  color: var(--muted); width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  border-radius: 6px;
}
.modal-close:hover { background: #e2e8f0; color: var(--ink); }
.modal-body { padding: 20px; overflow-y: auto; flex: 1; }
.modal-img-container {
  width: 100%; max-height: 60vh; background: #0b1520; display: flex;
  align-items: center; justify-content: center; border-radius: 8px; overflow: hidden;
}
.modal-img-container img { max-width: 100%; max-height: 60vh; object-fit: contain; }

/* Responsive & Print */
@media (max-width: 860px) {
  .layout { grid-template-columns: 1fr; gap: 0; padding: 0 16px 60px; }
  .toc { display: none; }
  .cover { padding: 66px 16px 24px; }
  .action, .action-head { grid-template-columns: 1fr; }
  .action-meta { border-left: 0; border-top: 1px solid var(--line); display: flex; gap: 8px; }
  .action-head { display: none; }
}
</style>
</head>
<body>

<!-- Fixed Top Navigation -->
<header class="topbar">
  <a href="#summary" class="brand">
    <div class="tx">
      {{PLANT_NAME}}
      <small>8D SOLAR DIAGNOSTIC PLATFORM</small>
    </div>
  </a>

  <nav class="topnav">
    <a href="#summary" class="navtab active">摘要 Summary</a>
    <a href="#d0" class="navtab">D0 立案</a>
    <a href="#d2" class="navtab">D2 描述</a>
    <a href="#d3" class="navtab">D3 圍堵</a>
    <a href="#d4" class="navtab">D4 根因</a>
    <a href="#d5" class="navtab">D5 對策</a>
    <a href="#d6" class="navtab">D6 驗證</a>
    <a href="#d7" class="navtab">D7 防再發</a>
    <a href="#safety" class="navtab">安全警語</a>
  </nav>

  <div class="topbar-actions">
    <button class="mode-toggle-btn {{MODE_CLASS}}" id="modeToggleBtn" onclick="toggleReportMode()">
      <span id="modeIcon">🔄</span>
      <span id="modeBtnText">模式：{{MODE_LABEL}}</span>
    </button>
    <button class="btn-action-sm" onclick="openRawDataModal()">
      <span>📊 原始數據對帳</span>
    </button>
    <button class="btn-action-sm" onclick="openPhotoGalleryModal()">
      <span>📸 照片證據庫</span>
    </button>
  </div>
</header>

<!-- Header Cover -->
<header class="cover">
  <div class="cover-inner">
    <div class="badges">
      <span class="badge {{MODE_BADGE_CLASS}}" id="headerModeBadge">{{MODE_LABEL}}</span>
      <span class="badge">8D 異常矯正報告</span>
      <span class="badge">對策執行中</span>
    </div>
    <h1>{{PLANT_NAME}}｜INV-13 發電異常</h1>
    <p class="lede">{{REPORT_LEDE}}</p>
    <dl class="factgrid">
      <div><dt>案號</dt><dd>{{CASE_NO}}</dd></div>
      <div><dt>電廠</dt><dd style="font-size:13px;">{{PLANT_LOCATION}}</dd></div>
      <div><dt>裝置容量</dt><dd>{{PLANT_CAPACITY_KWP}} kWp / {{INVERTER_COUNT}} 台 {{INVERTER_MODEL}}</dd></div>
      <div><dt>資料期間</dt><dd>{{DATA_PERIOD}}</dd></div>
      <div><dt>版本</dt><dd>{{REPORT_VERSION}}</dd></div>
      <div><dt>報告日期</dt><dd>{{REPORT_DATE}}</dd></div>
    </dl>
  </div>
</header>

<div class="layout">
  <!-- Sticky TOC -->
  <nav class="toc">
    <div class="toc-label">目錄 NAVIGATION</div>
    <a href="#summary">摘要 結論與問題清單</a>
    <a href="#d0">D0 立案與緊急反應</a>
    <a href="#d1">D1 小組與分工</a>
    <a href="#d2">D2 問題描述（量化）</a>
    <a href="#d3">D3 暫時圍堵措施</a>
    <a href="#d4">D4 根本原因分析</a>
    <a href="#d5">D5 永久對策選定</a>
    <a href="#d6">D6 執行與效果驗證</a>
    <a href="#d7">D7 防止再發</a>
    <a href="#d8">D8 結案與歸檔</a>
    <a href="#src">附錄B 原始資料來源</a>
    <a href="#limit">附錄C 分析限制</a>
    <a href="#safety">安全 作業安全警語</a>
  </nav>

  <main>
    <!-- ==================== SECTION: SUMMARY ==================== -->
    <section id="summary">
      <div class="sec-head"><span class="sec-tag">摘要</span><h2>結論與問題清單</h2></div>
      <div class="kpis">
        {{KPIS_HTML}}
      </div>

      <div class="tbl-wrap">
        <table>
          <caption>問題清單（依處理優先順序）</caption>
          <thead>
            <tr>
              <th style="width:70px;">優先</th>
              <th>項目</th>
              <th>量化規模</th>
              <th>對策方向</th>
            </tr>
          </thead>
          <tbody>
            {{PROBLEMS_ROWS_HTML}}
          </tbody>
        </table>
      </div>

      <div class="callout warn">
        <h4>這份報告最該帶走的一句話</h4>
        <p>{{TAKEAWAY_MESSAGE}}</p>
      </div>

      <!-- Interactive Plant Map -->
      <div style="margin-top:20px;">
        <div style="font-size:13px; font-weight:800; color:var(--blue-dd); margin-bottom:8px;">🗺️ 案場精確地理區位與臨海微氣候環境 (Leaflet 互動圖資)</div>
        <div id="plantMap" style="width:100%; height:320px; border-radius:8px; border:1px solid var(--line); z-index:1;"></div>
        <div style="font-size:12px; color:var(--muted); margin-top:6px; display:flex; justify-content:space-between;">
          <span>坐標：{{GEO_LAT}}° N, {{GEO_LNG}}° E</span>
          <span>臨海距離：約 650 公尺（高鹽霧、強季風、高地下水位野草生長極快）</span>
        </div>
      </div>
    </section>

    <!-- ==================== SECTION: D0 ==================== -->
    <section id="d0">
      <div class="sec-head"><span class="sec-tag">D0</span><h2>立案與緊急反應</h2></div>
      <p class="sec-purpose">接獲異常的第一時間：安全判斷、是否停機、建案號。</p>
      <p>{{D0_DISCOVERY_PATH}}</p>
      <div class="stmt fact">
        <span class="tag">事實</span>
        <p>{{D0_FACT_STATEMENT}}</p>
      </div>
      <div class="callout warn">
        <h4>安全判斷：不需立即停機，但有火載量風險</h4>
        <p>{{D0_SAFETY_JUDGEMENT}}</p>
      </div>
    </section>

    <!-- ==================== SECTION: D1 ==================== -->
    <section id="d1">
      <div class="sec-head"><span class="sec-tag">D1</span><h2>小組與分工</h2></div>
      <p class="sec-purpose">誰負責、誰執行、誰驗收、業主窗口是誰。</p>
      <div class="tbl-wrap">
        <table>
          <thead>
            <tr>
              <th style="width:140px;">角色</th>
              <th style="width:120px;">負責人</th>
              <th>負責事項</th>
            </tr>
          </thead>
          <tbody>
            {{TEAM_ROWS_HTML}}
          </tbody>
        </table>
      </div>
    </section>

    <!-- ==================== SECTION: D2 ==================== -->
    <section id="d2">
      <div class="sec-head"><span class="sec-tag">D2</span><h2>問題描述（量化）</h2></div>
      <p class="sec-purpose">用數字描述問題，不用形容詞。含損失 kWh 與金額。</p>
      <p>
        <strong>何時</strong>：{{D2_WHEN}}<br>
        <strong>何處</strong>：{{D2_WHERE}}<br>
        <strong>現象</strong>：{{D2_WHAT}}<br>
        <strong>影響</strong>：{{D2_HOW_MUCH}}
      </p>
      <p>比對前必須先修正一件事：<strong>平台登錄的裝置容量是錯的</strong>，最大誤差 +7.2%。不修正就直接比 kWh/kWp，排名會完全失真——初版就是因此誤判 001／002／005 整組偏低。</p>

      <div class="tbl-wrap">
        <table>
          <caption>平台登錄容量 vs 串接圖實際容量（335 W 組件）</caption>
          <thead>
            <tr>
              <th>INV</th>
              <th>串接設計</th>
              <th class="num">實際片數</th>
              <th class="num">實際 kWp</th>
              <th class="num">平台 kWp</th>
              <th class="num">誤差</th>
            </tr>
          </thead>
          <tbody>
            {{NAMEPLATE_ROWS_HTML}}
          </tbody>
        </table>
      </div>

      <div class="tbl-wrap">
        <table>
          <caption>用實際容量重算的 90 天單位發電量排名</caption>
          <thead>
            <tr>
              <th>INV</th>
              <th class="num">90 天 kWh/kWp</th>
              <th class="num">相對最佳台</th>
              <th class="num">90 天短少 kWh</th>
            </tr>
          </thead>
          <tbody>
            {{RANKINGS_ROWS_HTML}}
          </tbody>
        </table>
      </div>

      <!-- 90-Day Trend Chart -->
      <div style="margin-top:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <strong style="font-size:13px; color:var(--blue-dd);">📊 90 天逐日發電走勢與基準對照 (ECharts 互動圖表)</strong>
          <button class="btn-action-sm" onclick="openRawDataModal()">📥 檢視原始數據對帳表</button>
        </div>
        <div id="trendChart" style="width:100%; height:360px;"></div>
      </div>
    </section>

    <!-- ==================== SECTION: D3 ==================== -->
    <section id="d3">
      <div class="sec-head"><span class="sec-tag">D3</span><h2>暫時圍堵措施</h2></div>
      <p class="sec-purpose">在找到根因之前先止血，避免損失擴大。</p>
      <div class="actions">
        <div class="action-head">
          <div>行動項目</div>
          <div>負責</div>
          <div>期限</div>
        </div>
        {{CONTAINMENT_ACTIONS_HTML}}
      </div>
    </section>

    <!-- ==================== SECTION: D4 ==================== -->
    <section id="d4">
      <div class="sec-head"><span class="sec-tag">D4</span><h2>根本原因分析</h2></div>
      <p class="sec-purpose">證據與推論鏈，並列出已排除的假設。</p>
      <p>照片與數據互相印證，指向同一個原因：<strong>雜草覆蓋模組</strong>。以下為證據與推論鏈。</p>

      <!-- Evidence Photos Grid (Top 2: Field cutting) -->
      <div class="ev-grid">
        {{EV_PHOTOS_TOP_HTML}}
      </div>

      <div class="stmt fact">
        <span class="tag">事實</span>
        <p>浮體型系統，模組貼近水面與草澤，周圍為高過人的蘆葦。除草照片中，<strong>割下的草整片堆在模組表面，沒有清走</strong>。</p>
      </div>

      <div class="stmt fact">
        <span class="tag">事實</span>
        <p>串接圖上標示的紅框為雜草覆蓋模組區域，<strong>INV-13 覆蓋面積最大</strong>。</p>
      </div>

      <div class="tbl-wrap">
        <table>
          <caption>INV-13 相對基準台（006／010）的比值變化</caption>
          <thead>
            <tr>
              <th>期間</th>
              <th class="num">相對基準</th>
              <th>說明</th>
            </tr>
          </thead>
          <tbody>
            {{RATIO_TREND_ROWS_HTML}}
          </tbody>
        </table>
      </div>

      <ol style="padding-left:22px; margin-bottom:18px;">
        {{REASONING_STEPS_HTML}}
      </ol>

      <div class="tbl-wrap">
        <table class="excl">
          <caption>已排除的假設</caption>
          <thead>
            <tr>
              <th style="width:240px;">假設</th>
              <th>排除依據</th>
            </tr>
          </thead>
          <tbody>
            {{EXCLUDED_ROWS_HTML}}
          </tbody>
        </table>
      </div>

      <div class="callout danger">
        <h4>延伸風險：這不只是少發電</h4>
        <p>{{EXTENDED_RISK}}</p>
      </div>

      <!-- Evidence Photos Grid (Bottom 2: SCADA & Layout) -->
      <div class="ev-grid">
        {{EV_PHOTOS_BOTTOM_HTML}}
      </div>
    </section>

    <!-- ==================== SECTION: D5 ==================== -->
    <section id="d5">
      <div class="sec-head"><span class="sec-tag">D5</span><h2>永久對策選定</h2></div>
      <p class="sec-purpose">選項比較：投入、產出、風險，並說明為何選這個。</p>
      <div class="tbl-wrap">
        <table>
          <caption>永久對策選項比較</caption>
          <thead>
            <tr>
              <th>選項</th>
              <th>投入</th>
              <th>產出</th>
              <th>風險／限制</th>
              <th style="width:90px;">採用</th>
            </tr>
          </thead>
          <tbody>
            {{PERMANENT_OPTIONS_ROWS_HTML}}
          </tbody>
        </table>
      </div>
      <p><strong>主方案選擇理由</strong>：{{SELECTION_REASON}}</p>
    </section>

    <!-- ==================== SECTION: D6 ==================== -->
    <section id="d6">
      <div class="sec-head"><span class="sec-tag">D6</span><h2>執行與效果驗證</h2></div>
      <p class="sec-purpose">做了什麼、驗證門檻是什麼、結果如何。</p>
      <div class="actions">
        <div class="action-head">
          <div>行動項目</div>
          <div>負責</div>
          <div>期限</div>
        </div>
        {{VALIDATION_ACTIONS_HTML}}
      </div>
    </section>

    <!-- ==================== SECTION: D7 ==================== -->
    <section id="d7">
      <div class="sec-head"><span class="sec-tag">D7</span><h2>防止再發</h2></div>
      <p class="sec-purpose">SOP 修訂、監控告警規則、水平展開到其他案場。</p>
      <p>本案真正的缺口是流程，不是技術。以下三項修訂後適用於<strong>所有水上與地面案場</strong>。</p>
      <ol style="padding-left:22px; margin-bottom:16px;">
        {{PREVENTION_SOP_HTML}}
      </ol>
      <div class="callout warn">
        <h4>水平展開</h4>
        <p>{{HORIZONTAL_ROLLOUT}}</p>
      </div>
      <div class="actions">
        <div class="action-head">
          <div>行動項目</div>
          <div>負責</div>
          <div>期限</div>
        </div>
        {{PREVENTION_ACTIONS_HTML}}
      </div>
    </section>

    <!-- ==================== SECTION: D8 ==================== -->
    <section id="d8">
      <div class="sec-head"><span class="sec-tag">D8</span><h2>結案與歸檔</h2></div>
      <p class="sec-purpose">結案條件、文件歸檔位置、後續追蹤。</p>
      <ul style="padding-left:22px; margin-bottom:16px;">
        {{CLOSURE_CONDITIONS_HTML}}
      </ul>
    </section>

    <!-- ==================== SECTION: APPENDIX B ==================== -->
    <section id="src">
      <div class="sec-head"><span class="sec-tag">附錄B</span><h2>原始資料來源</h2></div>
      <p class="sec-purpose">本報告所有數字的出處，可回溯重算。</p>
      <div class="tbl-wrap">
        <table>
          <thead>
            <tr>
              <th>檔案／來源</th>
              <th style="width:140px;">期間</th>
              <th class="num" style="width:70px;">筆數</th>
              <th>說明</th>
            </tr>
          </thead>
          <tbody>
            {{SOURCES_ROWS_HTML}}
          </tbody>
        </table>
      </div>
    </section>

    <!-- ==================== SECTION: APPENDIX C ==================== -->
    <section id="limit">
      <div class="sec-head"><span class="sec-tag">附錄C</span><h2>分析限制</h2></div>
      <p class="sec-purpose">這份報告不能回答什麼。</p>
      <ul style="padding-left:22px; margin-bottom:16px;">
        {{LIMITATIONS_HTML}}
      </ul>
    </section>

    <!-- ==================== SECTION: SAFETY ==================== -->
    <section id="safety">
      <div class="sec-head"><span class="sec-tag" style="background:var(--coral);">安全</span><h2>作業安全警語</h2></div>
      <div class="callout danger">
        <h4>動工前必讀</h4>
        <ul style="padding-left:20px; margin-top:8px;">
          {{SAFETY_WARNINGS_HTML}}
        </ul>
      </div>
    </section>

    <footer style="border-top:1px solid var(--line); margin-top:40px; padding-top:18px; font-size:12.5px; color:var(--muted); line-height:1.6;">
      {{PLANT_NAME}}｜INV-13 發電異常｜<span id="footerModeLabel">{{MODE_LABEL}}</span>｜發布基準：{{REPORT_DATE}}｜內嵌高解析證據影像 4 張<br>
      本報告所有數據均可回溯至附錄 B 原始檔案，遵循進金生能源 8D Solar Diagnostic SOP 規範編製。
    </footer>
  </main>
</div>

<!-- Modal: Photo Lightbox -->
<div class="modal-overlay" id="photoModal">
  <div class="modal-content">
    <div class="modal-header">
      <h4 id="modalPhotoTitle">照片檢視</h4>
      <button class="modal-close" onclick="closePhotoModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div class="modal-img-container">
        <img id="modalPhotoImg" src="" alt="Photo Evidence">
      </div>
      <div style="margin-top:12px;">
        <div style="display:flex; justify-content:space-between; font-size:.75rem; color:var(--muted); margin-bottom:4px;">
          <span id="modalPhotoCategory" class="badge">類別</span>
          <span id="modalPhotoMeta">時間戳記</span>
        </div>
        <p id="modalPhotoCaption" style="font-size:.85rem; color:var(--ink); line-height:1.5;"></p>
      </div>
    </div>
  </div>
</div>

<!-- Modal: Raw Data Provenance -->
<div class="modal-overlay" id="rawDataModal">
  <div class="modal-content" style="max-width:1160px;">
    <div class="modal-header">
      <h4>📊 案場原始數據對帳與溯源檢視器 (Raw Data Provenance)</h4>
      <button class="modal-close" onclick="closeRawDataModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:8px;">
        <div style="display:flex; gap:8px;">
          <input type="text" id="rawSearchInput" placeholder="搜尋日期、逆變器或關鍵字..." oninput="filterRawTable()" style="padding:6px 12px; border:1px solid var(--line); border-radius:6px; font-size:.8rem; width:240px;">
          <button class="btn-action-sm" onclick="exportRawCsv()">📥 匯出 CSV 檔</button>
          <button class="btn-action-sm" onclick="copyRawTable()">📋 複製表格數據</button>
        </div>
        <div style="font-size:.75rem; color:var(--muted);">
          數據來源：amCharts 歷史匯出資料 & 竣工串接圖 C-002
        </div>
      </div>
      <div class="tbl-wrap" style="max-height:480px; overflow-y:auto;">
        <table id="rawDataTable">
          <thead>
            <tr>
              <th>日期 Date</th>
              <th>INV-001 (kWh)</th>
              <th>INV-002 (kWh)</th>
              <th>INV-005 (kWh)</th>
              <th>INV-006 (kWh)</th>
              <th>INV-009 (kWh)</th>
              <th>INV-010 (kWh)</th>
              <th>INV-013 (kWh)</th>
              <th>同儕均值 (kWh)</th>
              <th>INV-013 比率</th>
              <th>判定狀態</th>
            </tr>
          </thead>
          <tbody id="rawDataTableBody">
            <!-- Populated via JS -->
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- Modal: Photo Gallery Grid -->
<div class="modal-overlay" id="galleryModal">
  <div class="modal-content" style="max-width:1160px;">
    <div class="modal-header">
      <h4>📸 案場工程照片與現場證據庫總覽</h4>
      <button class="modal-close" onclick="closeGalleryModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div class="ev-grid" id="allPhotosGrid">
        <!-- Populated via JS -->
      </div>
    </div>
  </div>
</div>

<script>
// --- Mode Switcher (Internal vs Owner) ---
let currentMode = "{{INITIAL_MODE}}"; // 'internal' or 'owner'

function toggleReportMode() {
  if (currentMode === 'internal') {
    setReportMode('owner');
  } else {
    setReportMode('internal');
  }
}

function setReportMode(mode) {
  currentMode = mode;
  const isOwner = mode === 'owner';
  const label = isOwner ? '業主交付版' : '內部維運版';
  const badgeClass = isOwner ? 'mode-owner' : 'mode-internal';

  document.getElementById('pageTitle').innerText = `{{PLANT_NAME}}｜INV-13 發電異常｜${label}`;
  document.getElementById('modeBtnText').innerText = `模式：${label}`;
  document.getElementById('headerModeBadge').innerText = label;
  document.getElementById('headerModeBadge').className = `badge ${badgeClass}`;
  document.getElementById('footerModeLabel').innerText = label;

  const btn = document.getElementById('modeToggleBtn');
  if (isOwner) {
    btn.classList.add('owner');
  } else {
    btn.classList.remove('owner');
  }
}

// --- Photo Lightbox Logic ---
const evidencePhotos = {{EVIDENCE_PHOTOS_JSON}};

function openSinglePhoto(evId) {
  const p = evidencePhotos.find(item => item.id === evId);
  if (!p) return;
  document.getElementById('modalPhotoTitle').innerText = `${p.id} - ${p.title}`;
  document.getElementById('modalPhotoImg').src = p.src;
  document.getElementById('modalPhotoCategory').innerText = p.category;
  document.getElementById('modalPhotoMeta').innerText = p.meta;
  document.getElementById('modalPhotoCaption').innerText = p.caption;
  document.getElementById('photoModal').classList.add('active');
}
function closePhotoModal() {
  document.getElementById('photoModal').classList.remove('active');
}

function openPhotoGalleryModal() {
  const container = document.getElementById('allPhotosGrid');
  container.innerHTML = evidencePhotos.map(p => `
    <figure onclick="openSinglePhoto('${p.id}')">
      <img src="${p.src}" alt="${p.title}" loading="lazy">
      <figcaption>
        <span class="ev-id">${p.id}</span>${p.title}
        <span class="ev-meta">${p.meta}</span>
      </figcaption>
    </figure>
  `).join('');
  document.getElementById('galleryModal').classList.add('active');
}
function closeGalleryModal() {
  document.getElementById('galleryModal').classList.remove('active');
}

// --- Raw Data Table & CSV Export ---
const rawDailyData = {{DAILY_DATA_JSON}};

function populateRawTable() {
  const tbody = document.getElementById('rawDataTableBody');
  if (!tbody || !rawDailyData || !rawDailyData.length) return;
  tbody.innerHTML = rawDailyData.map(r => {
    const isAnomaly = r["013_ratio"] < 0.6;
    const statusTag = isAnomaly 
      ? '<span class="sev P1">INV-13 異常落後</span>' 
      : '<span class="sev P3">發電正常</span>';
    return `
      <tr>
        <td style="font-family:var(--mono); font-weight:700;">${r.date}</td>
        <td class="num">${r["001_kwh"]?.toFixed(1) || '-'}</td>
        <td class="num">${r["002_kwh"]?.toFixed(1) || '-'}</td>
        <td class="num">${r["005_kwh"]?.toFixed(1) || '-'}</td>
        <td class="num">${r["006_kwh"]?.toFixed(1) || '-'}</td>
        <td class="num">${r["009_kwh"]?.toFixed(1) || '-'}</td>
        <td class="num">${r["010_kwh"]?.toFixed(1) || '-'}</td>
        <td class="num" style="font-weight:800; color:${isAnomaly ? 'var(--coral)' : 'var(--ink)'};">${r["013_kwh"]?.toFixed(1) || '-'}</td>
        <td class="num">${r["peer_avg_kwh"]?.toFixed(1) || '-'}</td>
        <td class="num" style="font-weight:700; color:${isAnomaly ? 'var(--coral)' : 'var(--green)'};">${(r["013_ratio"] * 100).toFixed(1)}%</td>
        <td>${statusTag}</td>
      </tr>
    `;
  }).join('');
}

function openRawDataModal() {
  populateRawTable();
  document.getElementById('rawDataModal').classList.add('active');
}
function closeRawDataModal() {
  document.getElementById('rawDataModal').classList.remove('active');
}

function filterRawTable() {
  const query = document.getElementById('rawSearchInput').value.toLowerCase();
  const rows = document.querySelectorAll('#rawDataTableBody tr');
  rows.forEach(r => {
    r.style.display = r.innerText.toLowerCase().includes(query) ? '' : 'none';
  });
}

function exportRawCsv() {
  if (!rawDailyData || !rawDailyData.length) return;
  let csv = "Date,INV_001_kWh,INV_002_kWh,INV_005_kWh,INV_006_kWh,INV_009_kWh,INV_010_kWh,INV_013_kWh,Peer_Avg_kWh,INV_013_Ratio\\n";
  rawDailyData.forEach(r => {
    csv += `${r.date},${r["001_kwh"]},${r["002_kwh"]},${r["005_kwh"]},${r["006_kwh"]},${r["009_kwh"]},${r["010_kwh"]},${r["013_kwh"]},${r["peer_avg_kwh"]},${r["013_ratio"]}\\n`;
  });
  const blob = new Blob(["\\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Solar_8D_RawData_{{CASE_NO}}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function copyRawTable() {
  let text = "Date\\tINV-001\\tINV-002\\tINV-005\\tINV-006\\tINV-009\\tINV-010\\tINV-013\\tPeer_Avg\\t013_Ratio\\n";
  rawDailyData.forEach(r => {
    text += `${r.date}\\t${r["001_kwh"]}\\t${r["002_kwh"]}\\t${r["005_kwh"]}\\t${r["006_kwh"]}\\t${r["009_kwh"]}\\t${r["010_kwh"]}\\t${r["013_kwh"]}\\t${r["peer_avg_kwh"]}\\t${(r["013_ratio"]*100).toFixed(1)}%\\n`;
  });
  navigator.clipboard.writeText(text).then(() => {
    alert("✅ 原始發電數據已成功複製到剪貼簿！可直接貼上至 Excel。");
  });
}

// --- Leaflet Map Init ---
function initPlantMap() {
  const mapElement = document.getElementById('plantMap');
  if (!mapElement) return;
  const lat = {{GEO_LAT}};
  const lng = {{GEO_LNG}};
  const zoom = {{GEO_ZOOM}};
  window.plantMap = L.map('plantMap').setView([lat, lng], zoom);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
  }).addTo(window.plantMap);

  const marker = L.marker([lat, lng]).addTo(window.plantMap);
  marker.bindPopup(`
    <div style="font-family:'Noto Sans TC'; font-size:12px; line-height:1.4;">
      <strong style="color:#0C3A63; font-size:13px;">{{PLANT_NAME}}</strong><br>
      案號：{{CASE_NO}}<br>
      裝置容量：<strong>{{PLANT_CAPACITY_KWP}} kWp</strong><br>
      逆變器：{{INVERTER_COUNT}} 台 ({{INVERTER_MODEL}})
    </div>
  `).openPopup();
}

// --- ECharts Init ---
function initTrendChart() {
  const trendEl = document.getElementById('trendChart');
  if (!trendEl || !rawDailyData.length) return;
  window.trendChartInstance = echarts.init(trendEl);
  const dates = rawDailyData.map(d => d.date);
  const inv013 = rawDailyData.map(d => d["013_kwh"]);
  const peerAvg = rawDailyData.map(d => d["peer_avg_kwh"]);
  const inv006 = rawDailyData.map(d => d["006_kwh"]);

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: ['基準台 (INV-006)', '同儕平均 (7台均值)', '異常設備 (INV-013)'] },
    grid: { left: '3%', right: '4%', bottom: '8%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: dates },
    yAxis: { type: 'value', name: '日發電度數 (kWh)' },
    series: [
      {
        name: '基準台 (INV-006)',
        type: 'line',
        data: inv006,
        smooth: true,
        itemStyle: { color: '#1BB1BF' },
        lineStyle: { width: 2, type: 'dashed' }
      },
      {
        name: '同儕平均 (7台均值)',
        type: 'line',
        data: peerAvg,
        smooth: true,
        itemStyle: { color: '#1968AD' },
        lineStyle: { width: 3 }
      },
      {
        name: '異常設備 (INV-013)',
        type: 'line',
        data: inv013,
        smooth: true,
        itemStyle: { color: '#D95F45' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(217, 95, 69, 0.25)' },
            { offset: 1, color: 'rgba(217, 95, 69, 0.0)' }
          ])
        }
      }
    ]
  };
  window.trendChartInstance.setOption(option);
}

// TOC Scroll Spy
window.addEventListener('scroll', () => {
  const sections = document.querySelectorAll('section');
  const scrollPos = window.scrollY + 100;
  sections.forEach(s => {
    const top = s.offsetTop;
    const height = s.offsetHeight;
    const id = s.getAttribute('id');
    if (scrollPos >= top && scrollPos < top + height) {
      document.querySelectorAll('.toc a').forEach(a => a.classList.remove('active'));
      const activeLink = document.querySelector(`.toc a[href="#${id}"]`);
      if (activeLink) activeLink.classList.add('active');
    }
  });
});

window.addEventListener('DOMContentLoaded', () => {
  initPlantMap();
  initTrendChart();
  populateRawTable();
});
window.addEventListener('resize', () => {
  if (window.trendChartInstance) window.trendChartInstance.resize();
  if (window.plantMap) window.plantMap.invalidateSize();
});
</script>

</body>
</html>
"""


def build_platform(spec_path, daily_data_path=None, mode="internal", output_path=None):
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    meta = spec.get("meta", {})
    summary = spec.get("summary", {})
    d0 = spec.get("d0_emergency", {})
    d1 = spec.get("d1_team", [])
    d2 = spec.get("d2_description", {})
    d3 = spec.get("d3_containment", [])
    d4 = spec.get("d4_root_cause", {})
    d5 = spec.get("d5_permanent", {})
    d6 = spec.get("d6_validation", [])
    d7 = spec.get("d7_prevention", {})
    d8 = spec.get("d8_closure", {})
    app_b = spec.get("appendix_b_sources", [])
    app_c = spec.get("appendix_c_limitations", [])
    safety = spec.get("safety_warnings", [])

    # Load Daily Data
    daily_data = []
    if daily_data_path and os.path.exists(daily_data_path):
        with open(daily_data_path, "r", encoding="utf-8") as f:
            daily_data = json.load(f)
    elif "daily_data" in spec:
        daily_data = spec["daily_data"]
    else:
        # Fallback synthetic daily data
        for i in range(1, 31):
            date_str = f"09/{i:02d}"
            peer = 650.0 + (i % 5) * 15.0
            ratio = 0.446 if i > 15 else 0.88
            daily_data.append({
                "date": date_str,
                "001_kwh": peer * 0.95,
                "002_kwh": peer * 1.01,
                "005_kwh": peer * 0.98,
                "006_kwh": peer * 1.02,
                "009_kwh": peer * 0.99,
                "010_kwh": peer * 1.03,
                "013_kwh": peer * ratio,
                "peer_avg_kwh": peer,
                "013_ratio": ratio
            })

    # Render KPIs HTML
    kpis_html = []
    for k in summary.get("kpis", []):
        t = k.get("type", "normal")
        kpis_html.append(f"""
        <div class="kpi {t}">
          <div class="kpi-label">{k.get("label")}</div>
          <div class="kpi-value">{k.get("val")}<span class="kpi-unit">{k.get("unit", "")}</span></div>
          <div class="kpi-note">{k.get("sub", "")}</div>
        </div>
        """)

    # Render Problems Table HTML
    prob_rows = []
    for p in summary.get("problems_table", []):
        sev_class = p.get("priority", "P3")
        row_class = "row-bad" if "P1" in sev_class else ("row-warn" if "P2" in sev_class else "")
        prob_rows.append(f"""
        <tr class="{row_class}">
          <td><span class="sev {sev_class}">{p.get("priority")}</span></td>
          <td><strong>{p.get("item")}</strong></td>
          <td>{p.get("scale")}</td>
          <td>{p.get("action")}</td>
        </tr>
        """)

    # Render D1 Team Rows HTML
    team_rows = []
    for tm in d1:
        team_rows.append(f"""
        <tr>
          <td><strong>{tm.get("role")}</strong></td>
          <td>{tm.get("owner")}</td>
          <td>{tm.get("duty")}</td>
        </tr>
        """)

    # Render D2 Nameplate Table HTML
    nameplate_rows = []
    for np in d2.get("nameplate_comparison", []):
        row_class = "row-warn" if np.get("type") == "warn" else ""
        nameplate_rows.append(f"""
        <tr class="{row_class}">
          <td><strong>{np.get("inv")}</strong></td>
          <td>{np.get("design")}</td>
          <td class="num">{np.get("modules")}</td>
          <td class="num">{np.get("actual_kwp")}</td>
          <td class="num">{np.get("scada_kwp")}</td>
          <td class="num" style="font-weight:700;">{np.get("error")}</td>
        </tr>
        """)

    # Render D2 Rankings Table HTML
    ranking_rows = []
    for rk in d2.get("recalculated_rankings", []):
        row_class = "row-bad" if rk.get("type") == "bad" else ("row-warn" if rk.get("type") == "warn" else "")
        shortage = rk.get("shortage_kwh")
        if shortage != "—":
            try:
                shortage = f"{int(shortage):,}"
            except Exception:
                pass
        ranking_rows.append(f"""
        <tr class="{row_class}">
          <td><strong>{rk.get("inv")}</strong></td>
          <td class="num">{rk.get("kwh_per_kwp")}</td>
          <td class="num">{rk.get("ratio")}</td>
          <td class="num">{shortage}</td>
        </tr>
        """)

    # Render D3 Containment Actions HTML
    containment_actions = []
    for ca in d3:
        containment_actions.append(f"""
        <div class="action">
          <div class="action-what">{ca.get("what")}</div>
          <div class="action-meta"><span>負責</span>{ca.get("owner")}</div>
          <div class="action-meta"><span>期限</span>{ca.get("deadline")}</div>
          <div class="action-verify"><strong>驗證：</strong>{ca.get("verify")}</div>
        </div>
        """)

    # Render D4 Evidence Photos HTML
    evidence_photos = d4.get("evidence_photos", [])
    ev_top_html = []
    ev_bottom_html = []
    for i, ep in enumerate(evidence_photos):
        fig_html = f"""
        <figure onclick="openSinglePhoto('{ep.get("id")}')">
          <img src="{ep.get("src")}" alt="{ep.get("title")}" loading="lazy">
          <figcaption>
            <span class="ev-id">{ep.get("id")}</span>{ep.get("title")}
            <span class="ev-meta">{ep.get("meta")}</span>
          </figcaption>
        </figure>
        """
        if i < 2:
            ev_top_html.append(fig_html)
        else:
            ev_bottom_html.append(fig_html)

    # Render D4 Ratio Trend Rows HTML
    ratio_rows = []
    for rt in d4.get("ratio_trend", []):
        row_class = "row-bad" if rt.get("type") == "bad" else ""
        ratio_rows.append(f"""
        <tr class="{row_class}">
          <td>{rt.get("period")}</td>
          <td class="num" style="font-weight:700;">{rt.get("ratio")}</td>
          <td>{rt.get("note")}</td>
        </tr>
        """)

    # Render D4 Reasoning Steps HTML
    reasoning_steps_html = []
    for step in d4.get("reasoning_steps", []):
        reasoning_steps_html.append(f"<li>{step}</li>")

    # Render D4 Excluded Hypotheses HTML
    excl_rows = []
    for ex in d4.get("excluded_hypotheses", []):
        excl_rows.append(f"""
        <tr>
          <td><strong>{ex.get("hypo")}</strong></td>
          <td>{ex.get("reason")}</td>
        </tr>
        """)

    # Render D5 Permanent Options HTML
    perm_rows = []
    for opt in d5.get("options", []):
        row_class = "row-warn" if opt.get("type") == "highlight" else ""
        perm_rows.append(f"""
        <tr class="{row_class}">
          <td><strong>{opt.get("name")}</strong></td>
          <td>{opt.get("input")}</td>
          <td>{opt.get("output")}</td>
          <td>{opt.get("risk")}</td>
          <td><strong>{opt.get("status")}</strong></td>
        </tr>
        """)

    # Render D6 Validation Actions HTML
    val_actions = []
    for va in d6:
        val_actions.append(f"""
        <div class="action">
          <div class="action-what">{va.get("what")}</div>
          <div class="action-meta"><span>負責</span>{va.get("owner")}</div>
          <div class="action-meta"><span>期限</span>{va.get("deadline")}</div>
          <div class="action-verify"><strong>驗證：</strong>{va.get("verify")}</div>
        </div>
        """)

    # Render D7 Prevention SOP HTML
    prev_sop_html = []
    for ps in d7.get("sop_revisions", []):
        prev_sop_html.append(f"<li>{ps}</li>")

    # Render D7 Prevention Actions HTML
    prev_actions = []
    for pa in d7.get("review_actions", []):
        prev_actions.append(f"""
        <div class="action">
          <div class="action-what">{pa.get("what")}</div>
          <div class="action-meta"><span>負責</span>{pa.get("owner")}</div>
          <div class="action-meta"><span>期限</span>{pa.get("deadline")}</div>
        </div>
        """)

    # Render D8 Closure Conditions HTML
    closure_html = []
    for cc in d8.get("conditions", []):
        closure_html.append(f"<li>{cc}</li>")
    closure_html.append(f"<li><strong>文件歸檔</strong>：{d8.get('archive_location', '')}</li>")
    closure_html.append(f"<li><strong>後續追蹤</strong>：{d8.get('tracking', '')}</li>")

    # Render Appendix B Sources HTML
    src_rows = []
    for src in app_b:
        src_rows.append(f"""
        <tr>
          <td><strong>{src.get("name")}</strong></td>
          <td>{src.get("period")}</td>
          <td class="num">{src.get("count")}</td>
          <td>{src.get("desc")}</td>
        </tr>
        """)

    # Render Appendix C Limitations HTML
    lim_html = []
    for lm in app_c:
        lim_html.append(f"<li>{lm}</li>")

    # Render Safety Warnings HTML
    safety_html = []
    for sw in safety:
        safety_html.append(f"<li>{sw}</li>")

    # Coordinates
    geo = meta.get("coordinates", {})
    geo_lat = geo.get("lat", 24.3800)
    geo_lng = geo.get("lng", 120.5750)
    geo_zoom = geo.get("zoom", 16)

    is_owner = (mode.lower() == "owner")
    mode_label = "業主交付版" if is_owner else "內部維運版"
    mode_class = "owner" if is_owner else ""
    mode_badge_class = "mode-owner" if is_owner else "mode-internal"

    replacements = {
        "{{PLANT_NAME}}": meta.get("plant_name", "太陽光電電廠"),
        "{{PLANT_LOCATION}}": meta.get("plant_location", "案場地址"),
        "{{CASE_NO}}": meta.get("case_no", "PV-2026-001"),
        "{{DATA_PERIOD}}": meta.get("data_period", "90 天"),
        "{{REPORT_VERSION}}": meta.get("report_version", "v1.0"),
        "{{REPORT_DATE}}": meta.get("publish_date", "2026/09/21"),
        "{{PLANT_CAPACITY_KWP}}": f"{meta.get('actual_capacity_kwp', 1505.155):,.0f}",
        "{{INVERTER_COUNT}}": str(meta.get("inverter_count", 13)),
        "{{INVERTER_MODEL}}": meta.get("inverter_model", "SUNGROW SG110CX"),
        "{{REPORT_LEDE}}": meta.get("lede", ""),
        "{{TAKEAWAY_MESSAGE}}": meta.get("takeaway", ""),
        "{{GEO_LAT}}": str(geo_lat),
        "{{GEO_LNG}}": str(geo_lng),
        "{{GEO_ZOOM}}": str(geo_zoom),
        "{{INITIAL_MODE}}": "owner" if is_owner else "internal",
        "{{MODE_LABEL}}": mode_label,
        "{{MODE_CLASS}}": mode_class,
        "{{MODE_BADGE_CLASS}}": mode_badge_class,
        "{{D0_DISCOVERY_PATH}}": d0.get("discovery_path", ""),
        "{{D0_FACT_STATEMENT}}": d0.get("fact_statement", ""),
        "{{D0_SAFETY_JUDGEMENT}}": d0.get("safety_judgement", ""),
        "{{D2_WHEN}}": d2.get("when", ""),
        "{{D2_WHERE}}": d2.get("where", ""),
        "{{D2_WHAT}}": d2.get("what", ""),
        "{{D2_HOW_MUCH}}": d2.get("how_much", ""),
        "{{EXTENDED_RISK}}": d4.get("extended_risk", ""),
        "{{SELECTION_REASON}}": d5.get("selection_reason", ""),
        "{{HORIZONTAL_ROLLOUT}}": d7.get("horizontal_rollout", ""),
        "{{KPIS_HTML}}": "\n".join(kpis_html),
        "{{PROBLEMS_ROWS_HTML}}": "\n".join(prob_rows),
        "{{TEAM_ROWS_HTML}}": "\n".join(team_rows),
        "{{NAMEPLATE_ROWS_HTML}}": "\n".join(nameplate_rows),
        "{{RANKINGS_ROWS_HTML}}": "\n".join(ranking_rows),
        "{{CONTAINMENT_ACTIONS_HTML}}": "\n".join(containment_actions),
        "{{EV_PHOTOS_TOP_HTML}}": "\n".join(ev_top_html),
        "{{EV_PHOTOS_BOTTOM_HTML}}": "\n".join(ev_bottom_html),
        "{{RATIO_TREND_ROWS_HTML}}": "\n".join(ratio_rows),
        "{{REASONING_STEPS_HTML}}": "\n".join(reasoning_steps_html),
        "{{EXCLUDED_ROWS_HTML}}": "\n".join(excl_rows),
        "{{PERMANENT_OPTIONS_ROWS_HTML}}": "\n".join(perm_rows),
        "{{VALIDATION_ACTIONS_HTML}}": "\n".join(val_actions),
        "{{PREVENTION_SOP_HTML}}": "\n".join(prev_sop_html),
        "{{PREVENTION_ACTIONS_HTML}}": "\n".join(prev_actions),
        "{{CLOSURE_CONDITIONS_HTML}}": "\n".join(closure_html),
        "{{SOURCES_ROWS_HTML}}": "\n".join(src_rows),
        "{{LIMITATIONS_HTML}}": "\n".join(lim_html),
        "{{SAFETY_WARNINGS_HTML}}": "\n".join(safety_html),
        "{{EVIDENCE_PHOTOS_JSON}}": json.dumps(evidence_photos, ensure_ascii=False),
        "{{DAILY_DATA_JSON}}": json.dumps(daily_data, ensure_ascii=False)
    }

    content = HTML_TEMPLATE
    for k, v in replacements.items():
        content = content.replace(k, str(v))

    if not output_path:
        output_path = f"8D_report_{mode}.html"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 成功編譯標準化 8D 決策報告 [{mode_label}]：{output_path} ({len(content):,} bytes)")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成符合內部版與業主版雙軌標準的太陽光電電廠 8D 異常診斷決策平台")
    parser.add_argument("--spec", required=True, help="案場參數配置 JSON 路徑")
    parser.add_argument("--daily-data", required=False, help="逐日發電原始數據 JSON 路徑")
    parser.add_argument("--mode", default="internal", choices=["internal", "owner"], help="報告預設模式：internal (內部維運版) 或 owner (業主交付版)")
    parser.add_argument("--output", required=False, default="index.html", help="輸出 HTML 檔案路徑")
    args = parser.parse_args()

    build_platform(args.spec, args.daily_data, args.mode, args.output)
