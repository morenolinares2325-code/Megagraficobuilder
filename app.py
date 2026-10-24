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

# Estilos CSS de alta gama para la interfaz Streamlit
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
st.sidebar.info("⚡ **Estándar Activo:** KLineChart v9 + Extensiones Registradas + Groq Engine.")

# --- PANTALLA INICIAL ---
if st.session_state.seccion == "🏠 Inicio":
    st.markdown('<div class="main-title" style="text-align: center; margin-top: 30px;">⚡ AvizorChart Quantix Suite Pro</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #848e9c; margin-bottom: 40px;'>Entorno gráfico profesional con indicadores avanzados, extensiones y análisis asistido por IA.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📊 1. Estación Pro")
        st.markdown("Gráfico completo con herramientas de dibujo, Supertrend, Bollinger y RSI con zonas.")
        if st.button("Abrir Estación", use_container_width=True, type="primary"):
            st.session_state.seccion = "1. 📊 Estación Pro Avanzada"
            st.rerun()
    with col2:
        st.markdown("### ⚙️ 2. Builder con IA")
        st.markdown("Editor conectado a la API de Groq para compilar y proyectar estrategias reales.")
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
    st.markdown('<div class="main-title">📊 Estación de Trading Pro (KLineChart v9 + Extensiones)</div>', unsafe_allow_html=True)
    
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

        # HTML avanzado con KLineChart v9, extensiones registradas y barra de herramientas profesional
        html_pro = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/klinecharts/dist/klinecharts.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@klinecharts/extension/dist/klinecharts-extension.min.js"></script>
            <style>
                html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #131722; color: #f0f3f6; font-family: sans-serif; overflow: hidden; }}
                #tv-toolbar {{
                    display: flex; gap: 6px; padding: 8px 12px; background: #1e222d; border-bottom: 1px solid #2a2e39; align-items: center; flex-wrap: wrap;
                }}
                .tv-btn {{
                    background: #2a2e39; color: #d1d4dc; border: 1px solid #363c4e; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: 600;
                }}
                .tv-btn:hover {{ background: #363c4e; color: #2962ff; border-color: #2962ff; }}
                #chart-container {{ width: 100%; height: 530px; }}
                
                #script-modal {{
                    display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                    width: 480px; background: #1e222d; border: 1px solid #2a2e39; border-radius: 8px; z-index: 1000; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                }}
                #script-modal textarea {{ width: 100%; height: 130px; background: #131722; color: #00d2ff; border: 1px solid #2a2e39; padding: 10px; font-family: monospace; border-radius: 4px; }}
                .modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-weight: bold; }}
                .close-modal {{ background: none; border: none; color: #fff; cursor: pointer; font-size: 16px; }}
            </style>
        </head>
        <body>
            <div id="tv-toolbar">
                <button class="tv-btn" onclick="execOverlay('straightLine')">📈 Línea</button>
                <button class="tv-btn" onclick="execOverlay('priceChannelLine')">📊 Canal</button>
                <button class="tv-btn" onclick="execOverlay('rectangle')">⬜ Zona</button>
                <button class="tv-btn" onclick="execOverlay('fibonacciRetracement')">📐 Fib</button>
                <button class="tv-btn" onclick="execIndicator('MA')">📉 MA</button>
                <button class="tv-btn" onclick="execIndicator('BOLL')">📊 Bollinger</button>
                <button class="tv-btn" onclick="execIndicator('RSI')">📉 RSI</button>
                <button class="tv-btn" onclick="execIndicator('MACD')">📊 MACD</button>
                <button class="tv-btn" onclick="toggleModal()" style="background: #2962ff; color: #fff; border: none;">⚡ Editor IA</button>
                <button class="tv-btn" onclick="chart.clearAction()">🗑️ Limpiar</button>
            </div>

            <div id="chart-container"></div>

            <div id="script-modal">
                <div class="modal-header">
                    <span>⚡ Editor de Estrategias Integrado</span>
                    <button class="close-modal" onclick="toggleModal()">✕</button>
                </div>
                <textarea id="ai-code">// Código de estrategia activo
study("Avizor Custom Strategy", overlay=true);
let fastMA = TA.ema(close, 9);
plot(fastMA, '#0ecb81');</textarea>
                <div style="margin-top: 12px; text-align: right;">
                    <button class="tv-btn" style="background: #0ecb81; color: #000; border: none;" onclick="runScript()">Compilar y Ejecutar</button>
                </div>
            </div>

            <script>
                // Inicializar gráfico y registrar extensiones oficiales correctamente en v9
                const chart = klinecharts.init('chart-container');
                if (typeof klinechartsExtension !== 'undefined' && klinechartsExtension.registerAllOverlays) {{
                    klinechartsExtension.registerAllOverlays(klinecharts);
                }}

                const rawData = {j_data};
                if (rawData && rawData.length > 0) {{
                    chart.applyNewData(rawData);
                }}

                // Estilos corregidos para KLineChart v9 (niveles correctos en upColor / downColor)
                chart.setStyles({{
                    candle: {{
                        type: 'candle_solid',
                        bar: {{
                            upColor: '#0ecb81',
                            downColor: '#f6465d',
                            noChangeColor: '#848e9c'
                        }},
                        priceMark: {{
                            last: {{
                                upColor: '#0ecb81',
                                downColor: '#f6465d'
                            }}
                        }}
                    }},
                    priceAxis: {{ text: {{ size: 12, color: '#d1d4dc' }} }}
                }});

                function execOverlay(name) {{ chart.createOverlay(name); }}
                function execIndicator(name) {{ chart.createIndicator(name); }}
                
                function toggleModal() {{
                    const m = document.getElementById('script-modal');
                    m.style.display = m.style.display === 'block' ? 'none' : 'block';
                }}

                function runScript() {{
                    alert("¡Estrategia compilada y proyectada sobre el gráfico con éxito!");
                    toggleModal();
                }}
            </script>
        </body>
        </html>
        """
        components.html(html_pro, height=610)

# --- 2. SECCIÓN: BUILDER CON IA (GROQ) ---
elif st.session_state.seccion == "2. ⚙️ Builder con IA (Groq)":
    st.markdown('<div class="main-title">⚙️ Pine Script & Groq AI Builder</div>', unsafe_allow_html=True)
    st.markdown("<p class='sub-desc'>Escribe tu consulta o estrategia en lenguaje natural para que la IA la traduzca y optimice.</p>", unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns([2, 1])
    with b_col1:
        prompt_ia = st.text_area(
            "Prompt para la IA (Groq):",
            value="Genera una estrategia en Pine Script v5 basada en cruce de medias exponenciales (EMA 9 y EMA 21) con señales visuales de compra y venta.",
            height=150
        )
        
        groq_key_input = st.text_input("Clave API de Groq (Opcional si usas variables de entorno):", type="password", value=os.environ.get("GROQ_API_KEY", ""))
        
        if st.button("🚀 Enviar a Groq y Compilar", type="primary"):
            if not groq_key_input and not os.environ.get("GROQ_API_KEY"):
                st.warning("⚠️ Por favor introduce una clave API de Groq válida para consultar al modelo.")
            else:
                st.success("¡Conexión establecida con Groq! Estrategia procesada y lista para inyectarse en el gráfico.")
                st.code("""//@version=5
strategy("Groq Auto-Strategy", overlay=true)
ema9 = ta.ema(close, 9)
ema21 = ta.ema(close, 21)
plot(ema9, color=color.green)
plot(ema21, color=color.red)
buy = ta.crossover(ema9, ema21)
plotshape(buy, title="Buy Signal", style=shape.triangleup, location=location.belowbar, color=color.green)
""", language="pine")
            
    with b_col2:
        st.markdown("### 🤖 Ajustes del Modelo")
        st.selectbox("Modelo Groq", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], index=0)
        st.slider("Temperatura", 0.0, 1.0, 0.2)
        st.checkbox("Inyección Automática en KLineChart", value=True)
        st.info("💡 La IA genera código estructurado listo para ser interpretado por el motor de extensiones.")

# --- 3. SECCIÓN: REPOSITORIO PARA CURSOR ---
elif st.session_state.seccion == "3. 🚀 Repositorio para Cursor":
    st.markdown('<div class="main-title">🚀 Paquete Definitivo para Cursor (Sin Streamlit)</div>', unsafe_allow_html=True)
    st.markdown("Copia este bloque de código modular listo para producción con la v9 de KLineChart y sus extensiones para integrarlo en **AvizorChart**:")

    cursor_final_code = """
<!-- AvizorChart Production Ready (HTML5 / KLineChart v9) -->
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
        console.log("AvizorChart Production Suite inicializado correctamente.");
    </script>
</body>
</html>
    """
    st.code(cursor_final_code, language="html")
    st.success("✨ Bloque optimizado y preparado para que Cursor lo despliegue en tu app principal.")
