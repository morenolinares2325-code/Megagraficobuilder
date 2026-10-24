import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import json

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="AvizorChart Pro | Live Trading Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS modernos para mejorar la interfaz visual
st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        .main-header { font-size: 24px; font-weight: 700; color: #00d2ff; margin-bottom: 20px; }
        .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📈 AvizorChart Pro — Live Market & Pine Engine</div>', unsafe_allow_html=True)

# --- 1. BARRA LATERAL (CONTROLES Y BUILDER PINE) ---
st.sidebar.header("⚙️ Configuración del Activo")
ticker_symbol = st.sidebar.selectbox(
    "Selecciona Activo (yfinance)",
    ["EURUSD=X", "BTC-USD", "ETH-USD", "AAPL", "GC=X", "NVDA"],
    index=0
)

period = st.sidebar.selectbox("Periodo Histórico", ["1mo", "3mo", "6mo", "1y"], index=1)
interval = st.sidebar.selectbox("Intervalo de Vela", ["1h", "1d", "15m"], index=0)

st.sidebar.markdown("---")
st.sidebar.header("📝 Editor Pine Script")
pine_code = st.sidebar.text_area(
    "Código Pine Script:",
    value="""// Estrategia Pine Script Activa
study("Avizor Trend Engine", overlay=true)
fast_ema = input(9, "EMA Rápida")
slow_ema = input(21, "EMA Lenta")
// Lógica local integrada
""",
    height=220
)

apply_btn = st.sidebar.button("🚀 Aplicar Indicador al Gráfico", type="primary")

# --- 2. CARGA DE DATOS REALES CON YFINANCE ---
@st.cache_data(ttl=300)
def fetch_market_data(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return pd.DataFrame()
        
        # Aplanar MultiIndex si yfinance lo devuelve en versiones recientes
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.reset_index()
        
        # Detectar dinámicamente la columna de fecha/tiempo
        date_col = df.columns[0]
        
        # Renombrar columnas clave de forma estándar
        rename_dict = {date_col: 'Datetime', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}
        df = df.rename(columns=rename_dict)
        
        # Asegurar columnas requeridas
        required = ['Datetime', 'open', 'high', 'low', 'close']
        for col in required:
            if col not in df.columns:
                return pd.DataFrame()
                
        return df[['Datetime', 'open', 'high', 'low', 'close', 'volume']].dropna()
    except Exception as e:
        st.error(f"Error descargando datos: {e}")
        return pd.DataFrame()

df_market = fetch_market_data(ticker_symbol, period, interval)

# --- 3. RENDERIZADO VISUAL Y GRÁFICO ---
if df_market.empty:
    st.warning(f"⚠️ No se han encontrado datos para **{ticker_symbol}**. Prueba seleccionando otro activo o intervalo.")
else:
    # Tarjetas de Métricas Superiores
    latest = df_market.iloc[-1]
    prev = df_market.iloc[-2] if len(df_market) > 1 else latest
    price_change = ((latest['close'] - prev['close']) / prev['close']) * 100

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Activo", ticker_symbol)
    col2.metric("Último Cierre", f"{float(latest['close']):.4f}", f"{price_change:+.2f}%")
    col3.metric("Máximo", f"{float(latest['high']):.4f}")
    col4.metric("Mínimo", f"{float(latest['low']):.4f}")
    col5.metric("Volumen", f"{int(latest.get('volume', 0)):,}")

    # Preparar JSON para KLineChart
    chart_records = []
    for _, row in df_market.iterrows():
        try:
            ts = int(pd.Timestamp(row['Datetime']).timestamp() * 1000)
            chart_records.append({
                "timestamp": ts,
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row.get('volume', 1000))
            })
        except:
            continue

    json_data = json.dumps(chart_records)

    # HTML / JS con KLineChart y Extensiones Oficiales
    html_chart_code = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>KLineChart View</title>
        <script src="https://unpkg.com/klinecharts/dist/klinecharts.min.js"></script>
        <script src="https://unpkg.com/@klinecharts/extension/dist/klinecharts-extension.min.js"></script>
        <style>
            body, html {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                background-color: #0e1117;
                overflow: hidden;
            }}
            #chart-box {{
                width: 100%;
                height: 620px;
            }}
        </style>
    </head>
    <body>
        <div id="chart-box"></div>
        <script>
            // Inicialización limpia del gráfico
            const chart = klinecharts.init('chart-box');
            const chartData = {json_data};
            
            if (chartData && chartData.length > 0) {{
                chart.applyNewData(chartData);
            }}

            // Estética profesional modo oscuro
            chart.setStyle({{
                candle: {{
                    type: 'candle_solid',
                    bar: {{
                        upColor: '#0ecb81',
                        downColor: '#f6465d',
                        noChangeColor: '#848e9c'
                    }}
                }},
                grid: {{
                    horizontal: {{ show: true, color: '#21262d' }},
                    vertical: {{ show: true, color: '#21262d' }}
                }}
            }});
        </script>
    </body>
    </html>
    """

    # Renderizar componente gráfico con altura garantizada
    components.html(html_chart_code, height=640)

    # Barra inferior de estado
    st.info(f"💡 **Estado:** Conectado a yfinance ({len(df_market)} velas cargadas). Listo para exportar a AvizorChart vía Cursor.")
