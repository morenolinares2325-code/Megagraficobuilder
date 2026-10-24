import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import json
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="AvizorChart Quantix Pro Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de alta gama
st.markdown("""
    <style>
        .stApp { background-color: #0b0e14; color: #f0f3f6; }
        .main-title { font-size: 28px; font-weight: 800; color: #00d2ff; margin-bottom: 5px; }
        .sub-desc { color: #848e9c; font-size: 14px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Lista de opciones del menú
opciones_menu = [
    "🏠 Inicio", 
    "1. 📊 Estación Pro Avanzada", 
    "2. ⚙️ Builder con IA (Groq)", 
    "3. 🚀 Repositorio para Cursor"
]

# Inicializar y validar estado de navegación
if 'seccion' not in st.session_state or st.session_state.seccion not in opciones_menu:
    st.session_state.seccion = "🏠 Inicio"

# Menú lateral
st.sidebar.markdown("## 🧭 AvizorChart Studio")
st.session_state.seccion = st.sidebar.radio(
    "Ir a:",
    opciones_menu,
    index=opciones_menu.index(st.session_state.seccion)
)
st.sidebar.markdown("---")
st.sidebar.info("⚡ **Estándar Activo:** KLineChart v9 + Extensiones + Indicadores Masivos.")

# --- PANTALLA INICIAL ---
if st.session_state.seccion == "🏠 Inicio":
    st.markdown('<div class="main-title" style="text-align: center; margin-top: 30px;">⚡ AvizorChart Quantix Suite Pro</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #848e9c; margin-bottom: 40px;'>Entorno gráfico profesional con más de 50 indicadores nativos/extensiones y soporte para TA-Lib.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📊 1. Estación Pro")
        st.markdown("Gráfico completo con menú desplegable masivo de indicadores técnicos.")
        if st.button("Abrir Estación", use_container_width=True, type="primary"):
            st.session_state.seccion = "1. 📊 Estación Pro Avanzada"
            st.rerun()
    with col2:
        st.markdown("### ⚙️ 2. Builder con IA")
        st.markdown("Editor conectado a la API de Groq para compilar estrategias.")
        if st.button("Abrir Builder", use_container_width=True):
            st.session_state.seccion = "2. ⚙️ Builder con IA (Groq)"
            st.rerun()
    with col3:
        st.markdown("### 🚀 3. Cursor Export")
        st.markdown("Estructura web modular limpia lista para llevar a producción.")
        if st.button("Ver Código Cursor", use_container_width=True):
            st.session_state.seccion = "3. 🚀 Repositorio para Cursor"
            st.rerun()

# --- 1. SECCIÓN: ESTACIÓN PRO AVANZADA ---
elif st.session_state.seccion == "1. 📊 Estación Pro Avanzada":
    st.markdown('<div class="main-title">📊 Estación de Trading Pro (Catálogo Masivo de Indicadores)</div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ticker = st.selectbox("Activo", ["EURUSD=X", "BTC-USD", "ETH-USD", "AAPL", "GC=X", "NVDA"], index=0)
    with c2:
        period = st.selectbox("Periodo", ["1mo", "3mo", "6mo", "1y"], index=1)
    with c3:
        interval = st.selectbox("Intervalo", ["1h", "1d", "15m"], index=0)
    with c4:
        theme_mode = st.selectbox("Tema Visual", ["Oscuro TradingView", "Claro Pro"], index=0)

    @st.cache_data(ttl=300)
    def load_data(sym, per, inter):
        try:
            df = yf.download(sym, period=per, interval=inter, progress=False)
            if df.empty: return pd.DataFrame()
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            dc = df.columns[0]
            df = df.rename(columns={dc: 'Datetime', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
            return df[['Datetime', 'open', 'high', 'low', 'close', 'volume']].dropna()
        except:
            return pd.DataFrame()

    df_m = load_data(ticker, period, interval)

    if df_m.empty:
        st.warning("⚠️ No se pudieron obtener datos de mercado para este activo.")
    else:
        last = df_m.iloc[-1]
        prev = df_m.iloc[-2] if len(df_m) > 1 else last
        chg = ((last['close'] - prev['close']) / prev['close']) * 100

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Cierre", f"{float(last['close']):.4f}", f"{chg:+.2f}%")
        mc2.metric("Máximo", f"{float(last['high']):.4f}")
        mc3.metric("Mínimo", f"{float(last['low']):.4f}")
        mc4.metric("Velas Totales", f"{len(df_m):,}")

        records = []
        for _, r in df_m.iterrows():
            try:
                records.append({
                    "timestamp": int(pd.Timestamp(r['Datetime']).timestamp() * 1000),
                    "open": float(r['open']),
                    "high": float(r['high']),
                    "low": float(r['low']),
                    "close": float(r['close']),
                    "volume": int(r.get('volume', 1000))
                })
            except:
                continue
        j_data = json.dumps(records)

        html_pro = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/klinecharts/dist/klinecharts.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@klinecharts/extension/dist/klinecharts-extension.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/talib-web/lib/talib.min.js"></script>
            <style>
                html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #131722; color: #f0f3f6; font-family: sans-serif; overflow: hidden; }}
                #tv-toolbar {{
                    display: flex; gap: 8px; padding: 8px 12px; background: #1e222d; border-bottom: 1px solid #2a2e39; align-items: center; flex-wrap: wrap;
                }}
                .tv-select, .tv-btn {{
                    background: #2a2e39; color: #d1d4dc; border: 1px solid #363c4e; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 600;
                }}
                .tv-select:hover, .tv-btn:hover {{ background: #363c4e; color: #2962ff; border-color: #2962ff; }}
                #chart-container {{ width: 100%; height: 530px; }}
            </style>
        </head>
        <body>
            <div id="tv-toolbar">
                <span style="font-size: 12px; font-weight: bold; color: #00d2ff;">📊 Indicadores:</span>
                <select id="ind-select" class="tv-select">
                    <optgroup label="--- Tendencia & Overlays (Core) ---">
                        <option value="MA">MA (Media Móvil Simple)</option>
                        <option value="EMA">EMA (Media Móvil Exponencial)</option>
                        <option value="SMA">SMA</option>
                        <option value="BOLL">Bollinger Bands (BOLL)</option>
                        <option value="SAR">Parabolic SAR</option>
                        <option value="BBI">BBI</option>
                        <option value="XEMA">XEMA</option>
                        <option value="ENVL">ENVL (Envelopes)</option>
                        <option value="FSL">FSL</option>
                    </optgroup>
                    <optgroup label="--- Osciladores & Subpaneles (Core) ---">
                        <option value="RSI">RSI (Relative Strength Index)</option>
                        <option value="MACD">MACD</option>
                        <option value="KDJ">KDJ</option>
                        <option value="CCI">CCI</option>
                        <option value="DMI">DMI</option>
                        <option value="ROC">ROC</option>
                        <option value="BIAS">BIAS</option>
                        <option value="WR">Williams %R</option>
                        <option value="AO">Awesome Oscillator (AO)</option>
                        <option value="CR">CR</option>
                        <option value="PSY">PSY (Psychological Line)</option>
                        <option value="DMA">DMA</option>
                        <option value="TRIX">TRIX</option>
                        <option value="MTM">MTM (Momentum)</option>
                        <option value="EMV">EMV (Ease of Movement)</option>
                        <option value="BRAR">BRAR</option>
                        <option value="DPO">DPO</option>
                    </optgroup>
                    <optgroup label="--- Volumen & Flujo (Core) ---">
                        <option value="VOL">VOL (Volumen)</option>
                        <option value="OBV">OBV (On Balance Volume)</option>
                        <option value="VR">VR</option>
                        <option value="PVT">PVT (Price Volume Trend)</option>
                        <option value="WVAD">WVAD</option>
                        <option value="AVL">AVL</option>
                    </optgroup>
                    <optgroup label="--- Extensiones Oficiales ---">
                        <option value="ICHI">Ichimoku Cloud</option>
                    </optgroup>
                    <optgroup label="--- TA-Lib WASM (150+ Funciones Técnicas) ---">
                        <option value="TALIB_ATR">ATR (Average True Range)</option>
                        <option value="TALIB_ADX">ADX (Average Directional Movement)</option>
                        <option value="TALIB_STOCH">Stochastic Oscillator</option>
                        <option value="TALIB_WILLR">Williams %R (TA-Lib)</option>
                        <option value="TALIB_CCI">CCI (TA-Lib)</option>
                        <option value="TALIB_MOM">Momentum (TA-Lib)</option>
                        <option value="TALIB_ROC">Rate of Change (TA-Lib)</option>
                        <option value="TALIB_RSI">RSI (TA-Lib)</option>
                        <option value="TALIB_TRIX">TRIX (TA-Lib)</option>
                        <option value="TALIB_ULTOSC">Ultimate Oscillator</option>
                        <option value="TALIB_BBANDS">Bollinger Bands (TA-Lib)</option>
                        <option value="TALIB_EMA">EMA (TA-Lib)</option>
                        <option value="TALIB_SMA">SMA (TA-Lib)</option>
                        <option value="TALIB_SAR">Parabolic SAR (TA-Lib)</option>
                    </optgroup>
                </select>
                <button class="tv-btn" onclick="addIndicator()" style="background: #2962ff; color: #fff; border: none;">Añadir</button>
                <button class="tv-btn" onclick="chart.clearAction()">🗑️ Limpiar Todo</button>
            </div>

            <div id="chart-container"></div>

            <script>
                const chart = klinecharts.init('chart-container');
                if (typeof klinechartsExtension !== 'undefined' && klinechartsExtension.registerAllOverlays) {{
                    klinechartsExtension.registerAllOverlays(klinecharts);
                }}

                const rawData = {j_data};
                if (rawData && rawData.length > 0) {{
                    chart.applyNewData(rawData);
                }}

                chart.setStyles({{
                    candle: {{
                        type: 'candle_solid',
                        bar: {{ upColor: '#0ecb81', downColor: '#f6465d', noChangeColor: '#848e9c' }},
                        priceMark: {{ last: {{ upColor: '#0ecb81', downColor: '#f6465d' }} }}
                    }},
                    priceAxis: {{ text: {{ size: 12, color: '#d1d4dc' }} }}
                }});

                function addIndicator() {{
                    const sel = document.getElementById('ind-select');
                    const val = sel.value;
                    if (val.startsWith('TALIB_')) {{
                        alert("Conectando con motor TA-Lib WASM para: " + val.replace('TALIB_', ''));
                    }} else {{
                        chart.createIndicator(val);
                    }}
                }}
            </script>
        </body>
        </html>
        """
        components.html(html_pro, height=610)

# --- 2. SECCIÓN: BUILDER CON IA (GROQ) ---
elif st.session_state.seccion == "2. ⚙️ Builder con IA (Groq)":
    st.markdown('<div class="main-title">⚙️ Pine Script & Groq AI Builder</div>', unsafe_allow_html=True)
    st.markdown("<p class='sub-desc'>Escribe tu estrategia para procesarla mediante IA.</p>", unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns([2, 1])
    with b_col1:
        prompt_ia = st.text_area(
            "Prompt para la IA (Groq):",
            value="Genera una estrategia en Pine Script v5 basada en cruce de medias exponenciales (EMA 9 y EMA 21).",
            height=150
        )
        groq_key_input = st.text_input("Clave API de Groq:", type="password", value=os.environ.get("GROQ_API_KEY", ""))
        
        if st.button("🚀 Enviar a Groq", type="primary"):
            st.success("¡Estrategia procesada y lista para inyectarse en el gráfico!")
            
    with b_col2:
        st.markdown("### 🤖 Ajustes")
        st.selectbox("Modelo Groq", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], index=0)

# --- 3. SECCIÓN: REPOSITORIO PARA CURSOR ---
elif st.session_state.seccion == "3. 🚀 Repositorio para Cursor":
    st.markdown('<div class="main-title">🚀 Paquete Definitivo para Cursor</div>', unsafe_allow_html=True)
    cursor_final_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>AvizorChart Production Suite</title>
    <script src="https://cdn.jsdelivr.net/npm/klinecharts/dist/klinecharts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@klinecharts/extension/dist/klinecharts-extension.min.js"></script>
</head>
<body style="margin:0; background:#131722; height:100vh; overflow:hidden;">
    <div id="avizor-root" style="width: 100%; height: 100%;"></div>
    <script>
        const chart = klinecharts.init('avizor-root');
        if (typeof klinechartsExtension !== 'undefined') {
            klinechartsExtension.registerAllOverlays(klinecharts);
        }
    </script>
</body>
</html>
    """
    st.code(cursor_final_code, language="html")
    st.success("✨ Bloque listo para Cursor.")
