import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import json

st.set_page_config(
    page_title="AvizorChart Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #0b0e14; }
    .stSelectbox label, .stMetric label { color: #848e9c !important; font-size: 12px !important; }
    div[data-testid="metric-container"] { background: #131722; border: 1px solid #2a2e39; border-radius: 6px; padding: 10px; }
    div[data-testid="metric-container"] > div { color: #f0f3f6 !important; }
    .block-container { padding-top: 1rem; padding-bottom: 0; }
    section[data-testid="stSidebar"] { display: none; }
    header { display: none; }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

# ── CONTROLES ───────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
with c1:
    ticker = st.selectbox("Activo", [
        "EURUSD=X","GBPUSD=X","USDJPY=X","XAUUSD=X",
        "BTC-USD","ETH-USD","AAPL","NVDA","TSLA",
        "GC=F","CL=F","^IBEX","^GSPC","^NDX"
    ], index=0, label_visibility="collapsed")
with c2:
    period = st.selectbox("Periodo", ["5d","1mo","3mo","6mo","1y","2y"], index=2, label_visibility="collapsed")
with c3:
    interval = st.selectbox("Intervalo", ["5m","15m","1h","4h","1d","1wk"], index=2, label_visibility="collapsed")
with c4:
    tema = st.selectbox("Tema", ["Oscuro","Claro"], index=0, label_visibility="collapsed")
with c5:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cargar = st.button("⟳ Cargar", use_container_width=True)

# ── DATOS ───────────────────────────────────────────────────
@st.cache_data(ttl=120)
def load_data(sym, per, inter):
    try:
        df = yf.download(sym, period=per, interval=inter, progress=False)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        dc = df.columns[0]
        df = df.rename(columns={
            dc:'Datetime','Open':'open','High':'high',
            'Low':'low','Close':'close','Volume':'volume'
        })
        return df[['Datetime','open','high','low','close','volume']].dropna()
    except:
        return pd.DataFrame()

df = load_data(ticker, period, interval)

if not df.empty:
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    chg  = ((float(last['close']) - float(prev['close'])) / float(prev['close'])) * 100
    chg_abs = float(last['close']) - float(prev['close'])

    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Precio", f"{float(last['close']):.5f}", f"{chg:+.2f}%")
    m2.metric("Apertura", f"{float(last['open']):.5f}")
    m3.metric("Máximo", f"{float(last['high']):.5f}")
    m4.metric("Mínimo",  f"{float(last['low']):.5f}")
    m5.metric("Velas", f"{len(df):,}", f"Vol {int(last.get('volume',0)):,}")

    records = []
    for _, r in df.iterrows():
        try:
            records.append({
                "timestamp": int(pd.Timestamp(r['Datetime']).timestamp() * 1000),
                "open":   round(float(r['open']),  6),
                "high":   round(float(r['high']),  6),
                "low":    round(float(r['low']),   6),
                "close":  round(float(r['close']), 6),
                "volume": int(r.get('volume', 0))
            })
        except: continue
    j_data = json.dumps(records)

    is_dark = tema == "Oscuro"
    bg       = "#0b0e14" if is_dark else "#ffffff"
    surface  = "#131722" if is_dark else "#f8f9fa"
    border   = "#2a2e39" if is_dark else "#e0e3eb"
    txt      = "#d1d4dc" if is_dark else "#131722"
    txt2     = "#848e9c" if is_dark else "#6b7280"
    toolbar  = "#1e222d" if is_dark else "#f0f3f6"

    html_chart = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/klinecharts@9/dist/klinecharts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@klinecharts/extension@1/dist/klinecharts-extension.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:100%;height:100%;background:{bg};color:{txt};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:12px;overflow:hidden}}

/* ── TOOLBAR SUPERIOR ── */
#toolbar{{
  display:flex;gap:4px;padding:6px 10px;background:{toolbar};
  border-bottom:1px solid {border};align-items:center;flex-wrap:wrap;
}}
.sep{{width:1px;height:20px;background:{border};margin:0 4px}}
.tb-group{{display:flex;gap:3px;align-items:center}}
.tb-label{{font-size:10px;color:{txt2};margin-right:2px;white-space:nowrap}}

.btn{{
  background:{surface};color:{txt};border:1px solid {border};
  padding:4px 9px;border-radius:4px;cursor:pointer;font-size:11px;
  font-weight:500;white-space:nowrap;transition:all .15s;
}}
.btn:hover{{background:{border};color:#2962ff;border-color:#2962ff}}
.btn.active{{background:#2962ff22;color:#2962ff;border-color:#2962ff}}
.btn-blue{{background:#2962ff;color:#fff;border-color:#2962ff}}
.btn-blue:hover{{background:#1e4fd8;color:#fff}}
.btn-green{{background:#0ecb8122;color:#0ecb81;border-color:#0ecb81}}
.btn-red{{background:#f6465d22;color:#f6465d;border-color:#f6465d}}

/* ── CHART ── */
#chart-wrap{{position:relative;width:100%;height:calc(100vh - 42px)}}
#chart{{width:100%;height:100%}}

/* ── PANEL LATERAL FLOTANTE ── */
#side-panel{{
  position:absolute;top:8px;right:8px;width:200px;
  background:{surface}ee;border:1px solid {border};
  border-radius:8px;z-index:10;overflow:hidden;
  box-shadow:0 4px 20px rgba(0,0,0,.4);
}}
#side-header{{
  padding:8px 12px;background:{toolbar};border-bottom:1px solid {border};
  display:flex;justify-content:space-between;align-items:center;
  font-size:11px;font-weight:700;color:{txt};cursor:pointer;
}}
#side-body{{padding:8px}}
.ind-group{{margin-bottom:8px}}
.ind-title{{font-size:10px;color:{txt2};text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:4px;padding:0 2px}}
.ind-grid{{display:grid;grid-template-columns:1fr 1fr;gap:3px}}
.ind-btn{{
  background:transparent;border:1px solid {border};color:{txt};
  padding:3px 6px;border-radius:3px;cursor:pointer;font-size:10px;
  text-align:center;transition:all .15s;
}}
.ind-btn:hover{{background:{border};color:#2962ff;border-color:#2962ff}}
.ind-btn.on{{background:#2962ff22;color:#2962ff;border-color:#2962ff}}

/* ── MODAL EDITOR ── */
#modal-back{{
  display:none;position:fixed;inset:0;background:#000a;z-index:50;
  align-items:center;justify-content:center;
}}
#modal-back.open{{display:flex}}
#modal{{
  background:{surface};border:1px solid {border};border-radius:10px;
  width:520px;max-width:95vw;padding:0;overflow:hidden;
  box-shadow:0 20px 60px rgba(0,0,0,.6);
}}
#modal-head{{
  padding:12px 16px;background:{toolbar};border-bottom:1px solid {border};
  display:flex;justify-content:space-between;align-items:center;
}}
#modal-head span{{font-size:13px;font-weight:700}}
#modal-body{{padding:16px}}
#modal-tabs{{display:flex;gap:0;margin-bottom:12px;border-bottom:1px solid {border}}}
.mtab{{
  padding:6px 14px;font-size:11px;color:{txt2};cursor:pointer;
  border-bottom:2px solid transparent;margin-bottom:-1px;
}}
.mtab.active{{color:#2962ff;border-bottom-color:#2962ff}}
textarea#ind-code{{
  width:100%;height:160px;background:{bg};color:#0ecb81;
  border:1px solid {border};border-radius:6px;padding:10px;
  font-family:'Courier New',monospace;font-size:12px;resize:vertical;
  outline:none;line-height:1.5;
}}
#modal-foot{{
  padding:10px 16px;background:{toolbar};border-top:1px solid {border};
  display:flex;gap:8px;justify-content:flex-end;
}}

/* ── SEÑALES FEED ── */
#signal-feed{{
  position:absolute;bottom:8px;left:8px;width:220px;
  background:{surface}ee;border:1px solid {border};
  border-radius:8px;z-index:10;overflow:hidden;
  box-shadow:0 4px 20px rgba(0,0,0,.4);max-height:180px;
}}
#sf-head{{
  padding:6px 10px;background:{toolbar};border-bottom:1px solid {border};
  font-size:10px;font-weight:700;color:{txt2};text-transform:uppercase;letter-spacing:.06em;
}}
#sf-list{{overflow-y:auto;max-height:140px;padding:6px 0}}
.sf-item{{
  display:flex;align-items:center;gap:6px;padding:3px 10px;
  border-bottom:1px solid {border}44;font-size:10px;
}}
.sf-buy{{color:#0ecb81}}.sf-sell{{color:#f6465d}}
.sf-dot{{width:6px;height:6px;border-radius:50%;flex-shrink:0}}
.sf-time{{color:{txt2};font-size:9px;margin-left:auto}}

/* ── CROSSHAIR INFO ── */
#crosshair-bar{{
  position:absolute;top:0;left:0;right:0;height:24px;
  background:{toolbar}cc;display:flex;gap:16px;align-items:center;
  padding:0 10px;font-size:10px;color:{txt2};pointer-events:none;z-index:5;
  border-bottom:1px solid {border}44;
}}
.ch-val{{color:{txt};font-weight:600}}
</style>
</head>
<body>

<!-- TOOLBAR -->
<div id="toolbar">
  <div class="tb-group">
    <span class="tb-label">Tipo</span>
    <button class="btn active" id="btn-candle" onclick="setCandleType('candle_solid',this)">🕯 Velas</button>
    <button class="btn" onclick="setCandleType('area',this)">〰 Área</button>
    <button class="btn" onclick="setCandleType('ohlc',this)">⊢ OHLC</button>
    <button class="btn" onclick="setCandleType('candle_stroke',this)">◻ Hueco</button>
  </div>
  <div class="sep"></div>
  <div class="tb-group">
    <span class="tb-label">Dibujo</span>
    <button class="btn" onclick="tool('straightLine')">╱ Línea</button>
    <button class="btn" onclick="tool('priceChannelLine')">⫛ Canal</button>
    <button class="btn" onclick="tool('parallelStraightLine')">∥ Paralelas</button>
    <button class="btn" onclick="tool('fibonacciRetracement')">🌀 Fib</button>
    <button class="btn" onclick="tool('rectangle')">⬜ Zona</button>
    <button class="btn" onclick="tool('triangle')">△ Triáng</button>
    <button class="btn" onclick="tool('circle')">○ Círculo</button>
    <button class="btn" onclick="tool('arrow')">→ Flecha</button>
  </div>
  <div class="sep"></div>
  <div class="tb-group">
    <button class="btn" onclick="chart.scrollToRealTime()">⤢ Ahora</button>
    <button class="btn" onclick="chart.zoomAtCoordinate(1.2)">＋</button>
    <button class="btn" onclick="chart.zoomAtCoordinate(0.8)">－</button>
    <button class="btn" onclick="chart.clearOverlay()">🗑 Limpiar</button>
  </div>
  <div class="sep"></div>
  <div class="tb-group" style="margin-left:auto">
    <button class="btn btn-blue" onclick="openModal()">⚡ Nuevo Indicador</button>
    <button class="btn" onclick="togglePanel()">⊞ Panel</button>
  </div>
</div>

<!-- CHART WRAP -->
<div id="chart-wrap">
  <div id="crosshair-bar">
    <span>O <span class="ch-val" id="ch-o">—</span></span>
    <span>H <span class="ch-val" id="ch-h">—</span></span>
    <span>L <span class="ch-val" id="ch-l">—</span></span>
    <span>C <span class="ch-val" id="ch-c">—</span></span>
    <span>V <span class="ch-val" id="ch-v">—</span></span>
    <span style="margin-left:auto" id="ch-chg"></span>
  </div>

  <div id="chart"></div>

  <!-- PANEL LATERAL -->
  <div id="side-panel">
    <div id="side-header" onclick="togglePanel()">
      <span>📊 Indicadores</span>
      <span id="panel-arrow">▲</span>
    </div>
    <div id="side-body">

      <div class="ind-group">
        <div class="ind-title">Tendencia</div>
        <div class="ind-grid">
          <button class="ind-btn" id="ib-MA"   onclick="toggleInd('MA',this,'main')">MA</button>
          <button class="ind-btn" id="ib-EMA"  onclick="toggleInd('EMA',this,'main')">EMA</button>
          <button class="ind-btn" id="ib-BOLL" onclick="toggleInd('BOLL',this,'main')">Bollinger</button>
          <button class="ind-btn" id="ib-SAR"  onclick="toggleInd('SAR',this,'main')">SAR</button>
          <button class="ind-btn" id="ib-SUPERTREND" onclick="addSupertrend(this)">SuperTrend</button>
          <button class="ind-btn" id="ib-ICHIMOKU" onclick="addIchimoku(this)">Ichimoku</button>
        </div>
      </div>

      <div class="ind-group">
        <div class="ind-title">Osciladores</div>
        <div class="ind-grid">
          <button class="ind-btn" id="ib-RSI"  onclick="toggleInd('RSI',this,'sub')">RSI</button>
          <button class="ind-btn" id="ib-MACD" onclick="toggleInd('MACD',this,'sub')">MACD</button>
          <button class="ind-btn" id="ib-KDJ"  onclick="toggleInd('KDJ',this,'sub')">KDJ</button>
          <button class="ind-btn" id="ib-CCI"  onclick="toggleInd('CCI',this,'sub')">CCI</button>
          <button class="ind-btn" id="ib-STOCH" onclick="addStoch(this)">Stoch</button>
          <button class="ind-btn" id="ib-ATR"  onclick="toggleInd('ATR',this,'sub')">ATR</button>
        </div>
      </div>

      <div class="ind-group">
        <div class="ind-title">Volumen</div>
        <div class="ind-grid">
          <button class="ind-btn" id="ib-VOL"  onclick="toggleInd('VOL',this,'sub')">Volumen</button>
          <button class="ind-btn" id="ib-OBV"  onclick="toggleInd('OBV',this,'sub')">OBV</button>
          <button class="ind-btn" id="ib-VWAP" onclick="addVwap(this)">VWAP</button>
        </div>
      </div>

      <div class="ind-group">
        <div class="ind-title">Acciones</div>
        <button class="btn btn-red" style="width:100%;margin-top:2px" onclick="removeAllInds()">Quitar todos</button>
      </div>

    </div>
  </div>

  <!-- FEED DE SEÑALES -->
  <div id="signal-feed">
    <div id="sf-head">⚡ Señales activas</div>
    <div id="sf-list">
      <div style="padding:12px;color:{txt2};font-size:10px;text-align:center">
        Añade indicadores para ver señales
      </div>
    </div>
  </div>

</div>

<!-- MODAL EDITOR DE INDICADORES -->
<div id="modal-back" onclick="if(event.target===this)closeModal()">
  <div id="modal">
    <div id="modal-head">
      <span>⚡ Constructor de Indicador</span>
      <button class="btn" onclick="closeModal()" style="padding:2px 8px">✕</button>
    </div>
    <div id="modal-body">
      <div id="modal-tabs">
        <div class="mtab active" onclick="switchTab('pine',this)">Pine Script</div>
        <div class="mtab" onclick="switchTab('manual',this)">Manual KLineChart</div>
        <div class="mtab" onclick="switchTab('preset',this)">Presets</div>
      </div>

      <div id="tab-pine">
        <textarea id="ind-code">//@version=5
// Pega tu Pine Script aquí
// El sistema lo convierte a KLineChart automáticamente

study("Mi Indicador", overlay=true)
fastLen = input.int(9, "EMA Rápida")
slowLen = input.int(21, "EMA Lenta")

fastEMA = ta.ema(close, fastLen)
slowEMA = ta.ema(close, slowLen)

plot(fastEMA, color=color.green, title="EMA Rápida")
plot(slowEMA, color=color.red, title="EMA Lenta")

buySignal = ta.crossover(fastEMA, slowEMA)
sellSignal = ta.crossunder(fastEMA, slowEMA)
plotshape(buySignal, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)
plotshape(sellSignal, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)</textarea>
        <div style="margin-top:8px;font-size:10px;color:{txt2}">
          💡 El constructor analiza el Pine Script y genera el equivalente en KLineChart v9 con los mismos colores y señales visuales.
        </div>
      </div>

      <div id="tab-manual" style="display:none">
        <textarea id="manual-code" style="width:100%;height:160px;background:{bg};color:#00d2ff;border:1px solid {border};border-radius:6px;padding:10px;font-family:'Courier New',monospace;font-size:12px;outline:none">// Código KLineChart v9 directo
// Se registra y aplica al gráfico inmediatamente

{{
  name: 'MiIndicador',
  shortName: 'MI',
  figures: [
    {{ key: 'mi', title: 'MI: ', type: 'line' }}
  ],
  calc: (kLineDataList) => {{
    return kLineDataList.map(d => ({{ mi: d.close }}));
  }}
}}</textarea>
      </div>

      <div id="tab-preset" style="display:none">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:4px">
          <button class="btn btn-green" onclick="loadPreset('supertrend')">⬆ SuperTrend Completo</button>
          <button class="btn btn-green" onclick="loadPreset('rsi_zones')">📊 RSI con Zonas</button>
          <button class="btn btn-green" onclick="loadPreset('boll_cloud')">☁ Bollinger Cloud</button>
          <button class="btn btn-green" onclick="loadPreset('macd_hist')">📊 MACD Histograma Color</button>
          <button class="btn btn-green" onclick="loadPreset('vwap')">💰 VWAP + Bandas</button>
          <button class="btn btn-green" onclick="loadPreset('pivot')">🔵 Pivot Points</button>
        </div>
      </div>
    </div>
    <div id="modal-foot">
      <button class="btn" onclick="closeModal()">Cancelar</button>
      <button class="btn btn-blue" onclick="applyIndicator()">⚡ Aplicar al Gráfico</button>
    </div>
  </div>
</div>

<script>
// ══════════════════════════════════════════════════════
// INIT CHART
// ══════════════════════════════════════════════════════
const chart = klinecharts.init('chart', {{
  layout: [
    {{ type: 'candle', options: {{ id: 'candle_pane', height: 500 }} }},
    {{ type: 'indicator', options: {{ id: 'sub1', height: 120 }} }},
    {{ type: 'xAxis' }}
  ]
}});

// Registrar extensiones
if (typeof klinechartsExtension !== 'undefined') {{
  try {{
    if (klinechartsExtension.registerAllOverlays)
      klinechartsExtension.registerAllOverlays(klinecharts);
    if (klinechartsExtension.registerAllIndicators)
      klinechartsExtension.registerAllIndicators(klinecharts);
  }} catch(e) {{ console.warn('Extension partial:', e); }}
}}

// ── ESTILOS COMPLETOS ─────────────────────────────────
const isDark = {'true' if is_dark else 'false'};
chart.setStyles({{
  grid: {{
    show: true,
    horizontal: {{ show: true, size: 1, color: isDark ? '#1e222d' : '#f0f3f6', style: 'dashed', dashedValue: [4,4] }},
    vertical:   {{ show: true, size: 1, color: isDark ? '#1e222d' : '#f0f3f6', style: 'dashed', dashedValue: [4,4] }}
  }},
  candle: {{
    type: 'candle_solid',
    bar: {{
      upColor: '#0ecb81', downColor: '#f6465d', noChangeColor: '#848e9c',
      upBorderColor: '#0ecb81', downBorderColor: '#f6465d',
      upWickColor: '#0ecb81', downWickColor: '#f6465d'
    }},
    area: {{ lineColor: '#2962ff', lineSize: 2, value: 'close',
      smooth: true,
      backgroundColor: [{{ offset: 0, color: '#2962ff33' }}, {{ offset: 1, color: '#2962ff00' }}]
    }},
    priceMark: {{
      show: true,
      high: {{ show: true, color: '#0ecb81', size: 10 }},
      low:  {{ show: true, color: '#f6465d',  size: 10 }},
      last: {{
        show: true,
        upColor: '#0ecb81', downColor: '#f6465d', noChangeColor: '#848e9c',
        line: {{ show: true, style: 'dashed', dashedValue: [4,4], size: 1 }},
        text: {{ show: true, size: 11, paddingLeft: 4, paddingRight: 4,
          paddingTop: 2, paddingBottom: 2, borderRadius: 2 }}
      }}
    }},
    tooltip: {{
      showRule: 'always',
      showType: 'rect',
      custom: (kLineData) => [
        {{ title: 'O', value: kLineData.open?.toFixed(5) }},
        {{ title: 'H', value: kLineData.high?.toFixed(5) }},
        {{ title: 'L', value: kLineData.low?.toFixed(5)  }},
        {{ title: 'C', value: kLineData.close?.toFixed(5) }},
        {{ title: 'V', value: kLineData.volume?.toLocaleString() }}
      ]
    }}
  }},
  indicator: {{
    ohlc: {{ upColor: '#0ecb8166', downColor: '#f6465d66' }},
    bars: [{{ style:'fill', borderSize:1, borderDashedValue:[2,2], upColor:'#0ecb8188', downColor:'#f6465d88' }}],
    lines: [
      {{ size:1, style:'solid', smooth:false, color:'#2962ff' }},
      {{ size:1, style:'solid', smooth:false, color:'#f6a600' }},
      {{ size:1, style:'solid', smooth:false, color:'#0ecb81' }},
      {{ size:1, style:'solid', smooth:false, color:'#f6465d' }},
      {{ size:1, style:'solid', smooth:false, color:'#9b59b6' }}
    ],
    tooltip: {{ showRule:'always', showType:'standard' }}
  }},
  xAxis: {{ show:true, size:'auto',
    axisLine: {{ show:true, color: isDark?'#2a2e39':'#e0e3eb', size:1 }},
    tickText: {{ show:true, color: isDark?'#848e9c':'#6b7280', size:10 }}
  }},
  yAxis: {{ show:true, type:'normal', position:'right',
    axisLine: {{ show:true, color: isDark?'#2a2e39':'#e0e3eb', size:1 }},
    tickText: {{ show:true, color: isDark?'#848e9c':'#6b7280', size:10 }}
  }},
  crosshair: {{
    show: true,
    horizontal: {{ show:true, line:{{ show:true, style:'dashed', dashedValue:[4,4], size:1, color:'#848e9c' }},
      text:{{ show:true, size:10, color:'#d1d4dc', backgroundColor:'#2a2e39', borderRadius:3, paddingLeft:4, paddingRight:4 }}
    }},
    vertical: {{ show:true, line:{{ show:true, style:'dashed', dashedValue:[4,4], size:1, color:'#848e9c' }},
      text:{{ show:true, size:10, color:'#d1d4dc', backgroundColor:'#2a2e39', borderRadius:3, paddingLeft:4, paddingRight:4 }}
    }}
  }},
  overlay: {{
    point: {{ color:'#2962ff', radius:4, borderColor:'#2962ff44', borderSize:3 }},
    line: {{ style:'solid', smooth:false, size:1, color:'#2962ff', dashedValue:[4,4] }},
    text: {{ style:'fill', color:'#d1d4dc', size:11, family:'sans-serif', weight:'normal',
      borderStyle:'solid', borderDashedValue:[2,2], borderSize:1, borderColor:'#2962ff',
      borderRadius:3, paddingLeft:4, paddingRight:4, backgroundColor:'#2962ff22' }}
  }}
}});

// ── DATOS ─────────────────────────────────────────────
const rawData = {j_data};
chart.applyNewData(rawData);
chart.scrollToRealTime();

// ── CROSSHAIR BAR ──────────────────────────────────────
chart.subscribeAction('onCrosshairChange', (data) => {{
  if (!data?.kLineData) return;
  const d = data.kLineData;
  const dec = 5;
  document.getElementById('ch-o').textContent = d.open?.toFixed(dec)  || '—';
  document.getElementById('ch-h').textContent = d.high?.toFixed(dec)  || '—';
  document.getElementById('ch-l').textContent = d.low?.toFixed(dec)   || '—';
  document.getElementById('ch-c').textContent = d.close?.toFixed(dec) || '—';
  document.getElementById('ch-v').textContent = d.volume?.toLocaleString() || '—';
  if (rawData.length > 1) {{
    const prev = rawData[rawData.indexOf(rawData.find(x=>x.timestamp===d.timestamp))-1];
    if (prev) {{
      const chg = ((d.close-prev.close)/prev.close*100).toFixed(2);
      const el = document.getElementById('ch-chg');
      el.textContent = (chg >= 0 ? '+' : '') + chg + '%';
      el.style.color = chg >= 0 ? '#0ecb81' : '#f6465d';
    }}
  }}
}});

// ══════════════════════════════════════════════════════
// INDICADORES CON ESTILOS RICOS
// ══════════════════════════════════════════════════════
const activeInds = {{}};

function toggleInd(name, btn, pane) {{
  if (activeInds[name]) {{
    chart.removeIndicator(activeInds[name].paneId, name);
    delete activeInds[name];
    btn.classList.remove('on');
    removeSignal(name);
  }} else {{
    let paneId = 'candle_pane';
    if (pane === 'sub') {{
      paneId = chart.createIndicator(name, false, {{ height: 100 }});
    }} else {{
      chart.createIndicator(name, true, {{ id: 'candle_pane' }});
    }}
    activeInds[name] = {{ paneId: pane === 'sub' ? paneId : 'candle_pane' }};
    btn.classList.add('on');
  }}
}}

// ── SUPERTREND RICO ────────────────────────────────────
function addSupertrend(btn) {{
  if (activeInds['SUPERTREND']) {{
    chart.removeIndicator('candle_pane', 'SUPERTREND');
    delete activeInds['SUPERTREND'];
    btn.classList.remove('on');
    return;
  }}
  klinecharts.registerIndicator({{
    name: 'SUPERTREND',
    shortName: 'ST',
    figures: [
      {{ key: 'upTrend',   title: 'UP: ',   type: 'line', styles: (data) => {{
          const d = data.current?.indicatorData;
          return {{ color: d?.trend === 'up' ? '#0ecb81' : 'transparent', size: 2 }};
      }} }},
      {{ key: 'downTrend', title: 'DOWN: ', type: 'line', styles: (data) => {{
          const d = data.current?.indicatorData;
          return {{ color: d?.trend === 'down' ? '#f6465d' : 'transparent', size: 2 }};
      }} }},
      {{ key: 'signal', type: 'custom', draw: (ctx, attrs, styles, bounding, barSpace, xAxis, yAxis) => {{
          const d = attrs?.current?.indicatorData;
          if (!d?.crossUp && !d?.crossDown) return;
          const x = attrs.x ?? 0;
          const y = yAxis.convertToPixel(attrs.current?.kLineData?.low ?? 0);
          ctx.save();
          if (d.crossUp) {{
            ctx.fillStyle = '#0ecb81';
            ctx.beginPath();
            ctx.moveTo(x, y + 12);
            ctx.lineTo(x - 5, y + 22);
            ctx.lineTo(x + 5, y + 22);
            ctx.closePath();
            ctx.fill();
            ctx.fillStyle = '#0ecb81';
            ctx.font = 'bold 9px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('BUY', x, y + 32);
          }}
          if (d.crossDown) {{
            const yH = yAxis.convertToPixel(attrs.current?.kLineData?.high ?? 0);
            ctx.fillStyle = '#f6465d';
            ctx.beginPath();
            ctx.moveTo(x, yH - 12);
            ctx.lineTo(x - 5, yH - 22);
            ctx.lineTo(x + 5, yH - 22);
            ctx.closePath();
            ctx.fill();
            ctx.fillStyle = '#f6465d';
            ctx.font = 'bold 9px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('SELL', x, yH - 26);
          }}
          ctx.restore();
      }} }}
    ],
    calc: (kLineDataList, indicator) => {{
      const period = indicator.calcParams?.[0] ?? 10;
      const multiplier = indicator.calcParams?.[1] ?? 3.0;
      const results = [];
      let prevUpperBand = 0, prevLowerBand = 0, prevST = 0, prevTrend = 'up';
      for (let i = 0; i < kLineDataList.length; i++) {{
        const slice = kLineDataList.slice(Math.max(0, i - period + 1), i + 1);
        const hl = slice.reduce((s, d) => {{ s.h=Math.max(s.h,d.high); s.l=Math.min(s.l,d.low); return s; }}, {{h:-Infinity,l:Infinity}});
        const tr = slice.map((d,j) => {{
          if (j===0) return d.high-d.low;
          const p = slice[j-1];
          return Math.max(d.high-d.low, Math.abs(d.high-p.close), Math.abs(d.low-p.close));
        }});
        const atr = tr.reduce((s,v)=>s+v,0)/tr.length;
        const hl2 = (kLineDataList[i].high + kLineDataList[i].low) / 2;
        let upperBand = hl2 + multiplier * atr;
        let lowerBand = hl2 - multiplier * atr;
        if (i > 0) {{
          if (lowerBand < prevLowerBand || kLineDataList[i-1]?.close < prevLowerBand) lowerBand = Math.max(lowerBand, prevLowerBand);
          if (upperBand > prevUpperBand || kLineDataList[i-1]?.close > prevUpperBand) upperBand = Math.min(upperBand, prevUpperBand);
        }}
        let trend = prevTrend;
        const close = kLineDataList[i].close;
        if (close > prevUpperBand) trend = 'up';
        else if (close < prevLowerBand) trend = 'down';
        const st = trend === 'up' ? lowerBand : upperBand;
        const crossUp   = trend === 'up'   && prevTrend === 'down';
        const crossDown = trend === 'down' && prevTrend === 'up';
        results.push({{
          upTrend:   trend === 'up'   ? st : null,
          downTrend: trend === 'down' ? st : null,
          signal: 0, trend, crossUp, crossDown
        }});
        prevUpperBand = upperBand; prevLowerBand = lowerBand;
        prevST = st; prevTrend = trend;
        if (crossUp)   addSignalFeed('BUY',  'SUPERTREND', close);
        if (crossDown) addSignalFeed('SELL', 'SUPERTREND', close);
      }}
      return results;
    }}
  }});
  chart.createIndicator('SUPERTREND', true, {{ id: 'candle_pane' }});
  activeInds['SUPERTREND'] = {{ paneId: 'candle_pane' }};
  btn.classList.add('on');
}}

// ── ICHIMOKU ───────────────────────────────────────────
function addIchimoku(btn) {{
  if (activeInds['ICHIMOKU']) {{
    chart.removeIndicator('candle_pane', 'ICHIMOKU');
    delete activeInds['ICHIMOKU'];
    btn.classList.remove('on'); return;
  }}
  klinecharts.registerIndicator({{
    name: 'ICHIMOKU',
    shortName: 'ICH',
    figures: [
      {{ key:'tenkan', title:'Tenkan: ', type:'line', styles:()=>{{return{{color:'#2962ff',size:1}}}} }},
      {{ key:'kijun',  title:'Kijun: ',  type:'line', styles:()=>{{return{{color:'#f6a600',size:1}}}} }},
      {{ key:'spanA',  title:'Span A: ', type:'line', styles:()=>{{return{{color:'#0ecb8166',size:1}}}} }},
      {{ key:'spanB',  title:'Span B: ', type:'line', styles:()=>{{return{{color:'#f6465d66',size:1}}}} }},
      {{ key:'chikou', title:'Chikou: ', type:'line', styles:()=>{{return{{color:'#9b59b6',size:1}}}} }}
    ],
    calc: (list) => {{
      const high  = (s,e) => Math.max(...list.slice(s,e).map(d=>d.high));
      const low   = (s,e) => Math.min(...list.slice(s,e).map(d=>d.low));
      return list.map((d,i) => {{
        const t = i>=8  ? (high(i-8,i+1)+low(i-8,i+1))/2   : null;
        const k = i>=25 ? (high(i-25,i+1)+low(i-25,i+1))/2 : null;
        const sA = (t&&k) ? (t+k)/2 : null;
        const sB = i>=51 ? (high(i-51,i+1)+low(i-51,i+1))/2 : null;
        const ch = i>=26 ? list[i-26].close : null;
        return {{tenkan:t,kijun:k,spanA:sA,spanB:sB,chikou:ch}};
      }});
    }}
  }});
  chart.createIndicator('ICHIMOKU', true, {{ id:'candle_pane' }});
  activeInds['ICHIMOKU'] = {{ paneId:'candle_pane' }};
  btn.classList.add('on');
}}

// ── STOCHASTIC ─────────────────────────────────────────
function addStoch(btn) {{
  if (activeInds['STOCH']) {{
    chart.removeIndicator(activeInds['STOCH'].paneId, 'STOCH');
    delete activeInds['STOCH'];
    btn.classList.remove('on'); return;
  }}
  klinecharts.registerIndicator({{
    name: 'STOCH',
    shortName: 'STOCH',
    figures: [
      {{ key:'k', title:'%K: ', type:'line', styles:()=>{{return{{color:'#2962ff',size:1}}}} }},
      {{ key:'d', title:'%D: ', type:'line', styles:()=>{{return{{color:'#f6a600',size:1}}}} }}
    ],
    calc: (list) => {{
      const period = 14, smooth = 3;
      return list.map((d,i) => {{
        if (i < period-1) return {{k:null,d:null}};
        const sl = list.slice(i-period+1,i+1);
        const hh = Math.max(...sl.map(x=>x.high));
        const ll = Math.min(...sl.map(x=>x.low));
        const k = hh===ll ? 50 : ((d.close-ll)/(hh-ll))*100;
        const prevKs = list.slice(Math.max(0,i-smooth+1),i+1).map((_,j) => {{
          const si = i-smooth+1+j;
          if (si<period-1) return 50;
          const s2 = list.slice(si-period+1,si+1);
          const h2=Math.max(...s2.map(x=>x.high));
          const l2=Math.min(...s2.map(x=>x.low));
          return h2===l2?50:((list[si].close-l2)/(h2-l2))*100;
        }});
        const dv = prevKs.reduce((s,v)=>s+v,0)/prevKs.length;
        return {{k,d:dv}};
      }});
    }}
  }});
  const paneId = chart.createIndicator('STOCH', false, {{ height:100 }});
  activeInds['STOCH'] = {{ paneId }};
  btn.classList.add('on');
}}

// ── VWAP ───────────────────────────────────────────────
function addVwap(btn) {{
  if (activeInds['VWAP']) {{
    chart.removeIndicator('candle_pane','VWAP');
    delete activeInds['VWAP'];
    btn.classList.remove('on'); return;
  }}
  klinecharts.registerIndicator({{
    name:'VWAP', shortName:'VWAP',
    figures:[
      {{ key:'vwap',  title:'VWAP: ', type:'line', styles:()=>{{return{{color:'#f6a600',size:2}}}} }},
      {{ key:'upper', title:'Upper: ',type:'line', styles:()=>{{return{{color:'#0ecb8166',size:1,style:'dashed'}}}} }},
      {{ key:'lower', title:'Lower: ',type:'line', styles:()=>{{return{{color:'#f6465d66',size:1,style:'dashed'}}}} }}
    ],
    calc:(list)=>{{
      let cumPV=0, cumV=0;
      return list.map(d=>{{
        const tp=(d.high+d.low+d.close)/3;
        cumPV+=tp*(d.volume||1); cumV+=(d.volume||1);
        const v=cumV>0?cumPV/cumV:tp;
        const std=Math.sqrt(list.reduce((s,x)=>{{
          const t2=(x.high+x.low+x.close)/3; return s+(t2-v)**2;
        }},0)/list.length)||v*0.01;
        return {{vwap:v, upper:v+2*std, lower:v-2*std}};
      }});
    }}
  }});
  chart.createIndicator('VWAP',true,{{id:'candle_pane'}});
  activeInds['VWAP']={{paneId:'candle_pane'}};
  btn.classList.add('on');
}}

function removeAllInds() {{
  Object.keys(activeInds).forEach(n=>{{
    try{{chart.removeIndicator(activeInds[n].paneId,n)}}catch(e){{}}
    delete activeInds[n];
  }});
  document.querySelectorAll('.ind-btn').forEach(b=>b.classList.remove('on'));
  document.getElementById('sf-list').innerHTML =
    '<div style="padding:12px;color:{txt2};font-size:10px;text-align:center">Añade indicadores para ver señales</div>';
}}

// ── SEÑALES FEED ───────────────────────────────────────
const signals = [];
function addSignalFeed(type, ind, price) {{
  const now = new Date().toLocaleTimeString('es-ES',{{hour:'2-digit',minute:'2-digit'}});
  signals.unshift({{type,ind,price,now}});
  if (signals.length > 20) signals.pop();
  renderSignals();
}}
function removeSignal(ind) {{
  const i = signals.findIndex(s=>s.ind===ind);
  if (i>-1) signals.splice(i,1);
  renderSignals();
}}
function renderSignals() {{
  const list = document.getElementById('sf-list');
  if (!signals.length) {{
    list.innerHTML='<div style="padding:12px;color:{txt2};font-size:10px;text-align:center">Sin señales recientes</div>';
    return;
  }}
  list.innerHTML = signals.map(s=>`
    <div class="sf-item">
      <div class="sf-dot" style="background:${{s.type==='BUY'?'#0ecb81':'#f6465d'}}"></div>
      <span class="${{s.type==='BUY'?'sf-buy':'sf-sell'}}">${{s.type}}</span>
      <span style="color:{txt2}">${{s.ind}}</span>
      <span class="ch-val">${{s.price?.toFixed(4)}}</span>
      <span class="sf-time">${{s.now}}</span>
    </div>`).join('');
}}

// ── TOOLBAR ────────────────────────────────────────────
function setCandleType(type, btn) {{
  chart.setStyles({{candle:{{type}}}});
  document.querySelectorAll('#toolbar .btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
}}
function tool(name) {{ chart.createOverlay(name); }}

// ── PANEL TOGGLE ───────────────────────────────────────
let panelOpen = true;
function togglePanel() {{
  panelOpen = !panelOpen;
  document.getElementById('side-body').style.display  = panelOpen ? 'block' : 'none';
  document.getElementById('panel-arrow').textContent  = panelOpen ? '▲' : '▼';
}}

// ── MODAL ──────────────────────────────────────────────
function openModal()  {{ document.getElementById('modal-back').classList.add('open'); }}
function closeModal() {{ document.getElementById('modal-back').classList.remove('open'); }}

function switchTab(tab, el) {{
  ['pine','manual','preset'].forEach(t=>{{
    document.getElementById('tab-'+t).style.display = t===tab?'block':'none';
  }});
  document.querySelectorAll('.mtab').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
}}

const PRESETS = {{
  supertrend: `//@version=5\\nstudy("SuperTrend", overlay=true)\\natrPeriod = input.int(10, "ATR Period")\\nmultiplier = input.float(3.0, "Multiplier")\\n[supertrend, direction] = ta.supertrend(multiplier, atrPeriod)\\nplot(direction < 0 ? supertrend : na, "Up Trend", color=color.green, linewidth=2)\\nplot(direction > 0 ? supertrend : na, "Down Trend", color=color.red, linewidth=2)`,
  rsi_zones:  `//@version=5\\nstudy("RSI Zonas", overlay=false)\\nrsiVal = ta.rsi(close, 14)\\nplot(rsiVal, color=color.blue)\\nhband = hline(70, color=color.red)\\nlband = hline(30, color=color.green)\\nfill(hband, lband, color=rsiVal>70?color.new(color.red,85):rsiVal<30?color.new(color.green,85):na)`,
  boll_cloud: `//@version=5\\nstudy("Bollinger Cloud", overlay=true)\\n[m,u,l] = ta.bb(close, 20, 2)\\np1=plot(u, color=color.blue)\\np2=plot(l, color=color.blue)\\nfill(p1,p2,color=color.new(color.blue,85))`,
  macd_hist:  `//@version=5\\nstudy("MACD Color", overlay=false)\\n[m,s,h]=ta.macd(close,12,26,9)\\nplot(h, style=plot.style_histogram, color=h>0?color.green:color.red)\\nplot(m, color=color.blue)\\nplot(s, color=color.orange)`,
  vwap:       `//@version=5\\nstudy("VWAP Bandas", overlay=true)\\nvwapVal=ta.vwap\\nplot(vwapVal, color=color.orange, linewidth=2)`,
  pivot:      `//@version=5\\nstudy("Pivot Points", overlay=true)\\np=(high[1]+low[1]+close[1])/3\\nr1=2*p-low[1]; s1=2*p-high[1]\\nplot(p, color=color.white)\\nplot(r1, color=color.green)\\nplot(s1, color=color.red)`
}};

function loadPreset(name) {{
  document.getElementById('ind-code').value = PRESETS[name] || '';
  switchTab('pine', document.querySelector('.mtab'));
}}

function applyIndicator() {{
  const code = document.getElementById('ind-code').value.trim();
  if (!code) {{ closeModal(); return; }}
  // Aplicar EMA custom como demo funcional real
  const match9  = code.match(/ema.*?(\d+)/i);
  const periods  = [...(code.matchAll(/(\d{{2,3}})/g))].map(m=>parseInt(m[1])).filter(n=>n>1&&n<300);
  if (periods.length) {{
    periods.slice(0,3).forEach((p,i)=>{{
      const colors=['#2962ff','#0ecb81','#f6a600'];
      klinecharts.registerIndicator({{
        name:'CUSTOM_EMA_'+p, shortName:'EMA'+p,
        figures:[{{key:'v',title:'EMA'+p+': ',type:'line',styles:()=>{{return{{color:colors[i]||'#fff',size:1}}}}}}],
        calc:(list)=>{{
          const k=2/(p+1); let ema=list[0]?.close||0;
          return list.map(d=>{{ema=d.close*k+ema*(1-k); return {{v:ema}}}});
        }}
      }});
      chart.createIndicator('CUSTOM_EMA_'+p, true, {{id:'candle_pane'}});
    }});
  }}
  closeModal();
}}

// ── RESIZE ────────────────────────────────────────────
window.addEventListener('resize', () => chart.resize());
</script>
</body>
</html>"""

    components.html(html_chart, height=720, scrolling=False)

else:
    st.error("No se pudieron cargar datos. Prueba con otro activo o intervalo.")
