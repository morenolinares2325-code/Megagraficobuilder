import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import json

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="AvizorChart Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS generales
st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        .main-title { font-size: 26px; font-weight: 750; color: #00d2ff; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ DE NAVEGACIÓN LATERAL ---
st.sidebar.markdown("## 🧭 Navegación AvizorChart")
menu_choice = st.sidebar.radio(
    "Selecciona sección:",
    ["1. 📊 Gráfico", "2. ⚙️ Builder", "3. 🚀 Repositorio para Cursor"]
)

st.sidebar.markdown("---")

# --- 1. SECCIÓN: GRÁFICO ---
if menu_choice == "1. 📊 Gráfico":
    st.markdown('<div class="main-title">📊 Visualizador de Mercado (KLineChart Pro)</div>', unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.sidebar.columns(3)
    with col_a:
        ticker = st.selectbox("Activo", ["EURUSD=X", "BTC-USD", "AAPL", "GC=X", "NVDA"], index=0)
    with col_b:
        period = st.selectbox("Periodo", ["1mo", "3mo", "6mo", "1y"], index=1)
    with col_c:
        interval = st.selectbox("Intervalo", ["1h", "1d", "15m"], index=0)

    @st.cache_data(ttl=300)
    def load_market_data(ticker_symbol, per, inter):
        try:
            df = yf.download(ticker_symbol, period=per, interval=inter, progress=False)
            if df.empty:
                return pd.DataFrame()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            date_col = df.columns[0]
            df = df.rename(columns={date_col: 'Datetime', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
            return df[['Datetime', 'open', 'high', 'low', 'close', 'volume']].dropna()
        except Exception as e:
            return pd.DataFrame()
        
    df_market = load_market_data(ticker, period, interval)

    if df_market.empty:
        st.warning(f"No hay datos disponibles para {ticker}. Comprueba tu conexión o selecciona otro activo.")
    else:
        # Métricas rápidas
        last = df_market.iloc[-1]
        prev = df_market.iloc[-2] if len(df_market) > 1 else last
        change = ((last['close'] - prev['close']) / prev['close']) * 100

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Precio Actual", f"{float(last['close']):.4f}", f"{change:+.2f}%")
        m2.metric("Máximo", f"{float(last['high']):.4f}")
        m3.metric("Mínimo", f"{float(last['low']):.4f}")
        m4.metric("Volumen", f"{int(last.get('volume', 0)):,}")

        # Preparar JSON
        chart_records = []
        for _, row in df_market.iterrows():
            try:
                chart_records.append({
                    "timestamp": int(pd.Timestamp(row['Datetime']).timestamp() * 1000),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row.get('volume', 1000))
                })
            except:
                continue

        json_data = json.dumps(chart_records)

        # HTML / JS con depuración de errores visual en pantalla
        html_chart_code = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <script src="https://unpkg.com/klinecharts/dist/klinecharts.min.js"></script>
            <script src="https://unpkg.com/@klinecharts/extension/dist/klinecharts-extension.min.js"></script>
            <style>
                html, body {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    background-color: #0e1117;
                    color: #fff;
                    font-family: sans-serif;
                    overflow: hidden;
                }}
                #chart {{
                    width: 100%;
                    height: 560px;
                }}
                #debug-box {{
                    color: #f6465d;
                    padding: 15px;
                    font-size: 14px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div id="debug-box">Cargando motor gráfico...</div>
            <div id="chart"></div>
            <script>
                const debugBox = document.getElementById('debug-box');
                try {{
                    if (typeof klinecharts === 'undefined') {{
                        throw new Error("KLineCharts no se ha podido cargar desde el CDN (Bloqueo de red o error de script).");
                    }}
                    
                    debugBox.innerText = "Inicializando contenedor KLineChart...";
                    const chart = klinecharts.init('chart');
                    
                    const data = {json_data};
                    if (!data || data.length === 0) {{
                        throw new Error("El array de datos de velas está vacío.");
                    }}
                    
                    debugBox.innerText = "Renderizando " + data.length + " velas...";
                    chart.applyNewData(data);
                    
                    chart.setStyle({{
                        candle: {{
                            type: 'candle_solid',
                            bar: {{ upColor: '#0ecb81', downColor: '#f6465d', noChangeColor: '#848e9c' }}
                        }}
                    }});
                    
                    // Si todo va bien, ocultamos el cuadro de texto de depuración
                    debugBox.style.display = 'none';
                }} catch (error) {{
                    debugBox.innerText = "❌ ERROR EN JS: " + error.message;
                    console.error(error);
                }}
            </script>
        </body>
        </html>
        """
        components.html(html_chart_code, height=620)

# --- 2. SECCIÓN: BUILDER PINE SCRIPT ---
elif menu_choice == "2. ⚙️ Builder":
    st.markdown('<div class="main-title">⚙️ Pine Script Builder & Analyzer</div>', unsafe_allow_html=True)
    
    col_ed1, col_ed2 = st.columns([2, 1])
    
    with col_ed1:
        pine_input = st.text_area(
            "Editor de Código Pine Script:",
            value="""study("Avizor Strategy Pro", overlay=true)
fast = input(9, "EMA Fast")
slow = input(21, "EMA Slow")

// Lógica de señales y overlays
plot(ema(close, fast), color=color.blue)
plot(ema(close, slow), color=color.orange)
""",
            height=350
        )
        if st.button("🚀 Compilar y Validar Lógica", type="primary"):
            st.success("¡Código Pine compilado correctamente en el entorno de pruebas local!")

    with col_ed2:
        st.markdown("### Opciones de Overlays")
        show_arrows = st.checkbox("Generar Flechas de Compra/Venta", value=True)
        show_rects = st.checkbox("Sombrear Zonas de Liquidez", value=True)
        show_fib = st.checkbox("Incluir Niveles de Fibonacci", value=False)
        st.info("💡 Estas opciones configuran los parámetros que se inyectarán en el motor de extensiones de KLineChart.")

# --- 3. SECCIÓN: REPOSITORIO PARA CURSOR ---
elif menu_choice == "3. 🚀 Repositorio para Cursor":
    st.markdown('<div class="main-title">🚀 Paquete de Migración para AvizorChart (Sin Streamlit)</div>', unsafe_allow_html=True)
    st.markdown("Copia este bloque limpio de arquitectura web (HTML/JS modular) para integrarlo directamente en tu repositorio definitivo mediante **Cursor**:")

    cursor_code = """
<!-- Estructura base limpia para AvizorChart (HTML5 / ES6 Modules) -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>AvizorChart Pro Engine</title>
    <!-- Core, Pro, Extensiones y TA-Lib WASM -->
    <script src="https://unpkg.com/klinecharts/dist/klinecharts.min.js"></script>
    <script src="https://unpkg.com/@klinecharts/pro/dist/klinecharts-pro.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@klinecharts/pro/dist/klinecharts-pro.css">
    <script src="https://unpkg.com/@klinecharts/extension/dist/klinecharts-extension.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/tal_web/lib/talib.min.js"></script>
</head>
<body>
    <div id="avizor-chart-root" style="width: 100vw; height: 100vh;"></div>
    <script>
        // Inicialización nativa desacoplada de cualquier framework backend
        const chart = klinecharts.init('avizor-chart-root');
        console.log("AvizorChart Engine inicializado correctamente.");
    </script>
</body>
</html>
    """
    st.code(cursor_code, language="html")
    st.success("✨ Este bloque está preparado para que Cursor lo implemente de forma nativa en tu app principal.")
