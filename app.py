import streamlit as st
import streamlit.components.v1 as components

# Configuración inicial de la página
st.set_page_config(
    page_title="Avizor Builder Pro - Test Indicador",
    layout="wide"
)

st.title("🛠️ Avizor Builder Pro: Depuración de Indicador")

if "render_trigger" not in st.session_state:
    st.session_state.render_trigger = False

class IndicatorBuilderEngine:
    def __init__(self):
        self.version = "2.6.0"

    def parse_to_klinechart(self, mode: str, raw_code: str) -> str:
        if mode == "KLineChart (JS/TS)":
            return raw_code
        
        # Indicador de prueba limpio y 100% compatible superpuesto en el precio
        return raw_code

engine = IndicatorBuilderEngine()

def get_chart_html(indicator_script: str = ""):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>KLineCharts Debug Test</title>
        <script src="https://cdn.jsdelivr.net/npm/klinecharts/dist/klinecharts.min.js"></script>
        <style>
            body, html {
                margin: 0; padding: 0;
                background-color: #0d1117; color: #c9d1d9;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                overflow: hidden;
            }
            #chart { width: 100vw; height: 680px; }
            #debug-panel {
                background: #161b22; color: #58a6ff; padding: 10px 16px;
                font-family: 'Courier New', Courier, monospace; font-size: 13px;
                border-top: 1px solid #30363d; display: flex; justify-content: space-between;
                align-items: center; height: 45px;
            }
            .status-ok { color: #3fb950; font-weight: bold; }
            .status-err { color: #f85149; font-weight: bold; }
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <div id="debug-panel">
            <span id="status-text">Estado: Iniciando prueba de indicador...</span>
            <span id="candles-count">Velas: 0</span>
        </div>

        <script>
            let chart;
            const statusText = document.getElementById('status-text');
            const candlesCount = document.getElementById('candles-count');

            function setStatus(msg, isError = false) {
                statusText.className = isError ? 'status-err' : 'status-ok';
                statusText.innerText = ">> " + msg;
            }

            window.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    try {
                        if (typeof klinecharts === 'undefined') {
                            throw new Error("La librería klinecharts no se cargó correctamente.");
                        }

                        chart = klinecharts.init('chart', {
                            styles: {
                                grid: {
                                    horizontal: { show: true, color: '#21262d' },
                                    vertical: { show: true, color: '#21262d' }
                                },
                                candle: {
                                    bar: {
                                        upColor: '#238636',
                                        downColor: '#da3633',
                                        noChangeColor: '#8b949e'
                                    }
                                }
                            }
                        });
                        
                        setStatus("Generando histórico EURUSD...");

                        let baseTime = Date.now() - (300 * 24 * 60 * 60 * 1000); 
                        let basePrice = 1.0850;
                        let mockData = [];

                        for (let i = 0; i < 300; i++) {
                            let variation = (Math.random() - 0.49) * 0.003;
                            let open = basePrice;
                            let close = open + variation;
                            let high = Math.max(open, close) + Math.random() * 0.0015;
                            let low = Math.min(open, close) - Math.random() * 0.0015;

                            mockData.push({
                                timestamp: baseTime + (i * 24 * 60 * 60 * 1000),
                                open: parseFloat(open.toFixed(5)),
                                high: parseFloat(high.toFixed(5)),
                                low: parseFloat(low.toFixed(5)),
                                close: parseFloat(close.toFixed(5)),
                                volume: Math.floor(Math.random() * 50000)
                            });
                            basePrice = close;
                        }

                        chart.applyNewData(mockData);
                        candlesCount.innerText = "Velas: " + mockData.length;
                        setStatus("Histórico aplicado con éxito.");

                        /* --- INYECCIÓN DEL SCRIPT DEL INDICADOR --- */
                        REPLACE_INDICATOR_SCRIPT
                        
                        setStatus("¡Indicador inyectado correctamente en el gráfico principal!");
                    } catch (e) {
                        setStatus("Error: " + e.message, true);
                    }
                }, 250);
            });
        </script>
    </body>
    </html>
    """
    return html_template.replace("REPLACE_INDICATOR_SCRIPT", indicator_script)

# --- Interfaz de Streamlit ---
col_editor, col_chart = st.columns([1, 1.6])

with col_editor:
    st.subheader("⚙️ Editor de Indicador Directo")
    
    selected_mode = st.selectbox(
        "Modo de Lenguaje:",
        ["KLineChart (JS/TS)", "Pine Script", "MQL5", "cTrader (C#)"]
    )
    
    # Código de prueba robusto y limpio que dibuja una media móvil simple y puntos de señal directos sobre el precio
    default_code = """if (typeof klinecharts !== 'undefined' && chart) {
    klinecharts.registerIndicator({
        name: "AVIZOR_SIMPLE_TEST",
        shortName: "Test SMA + Signals",
        series: 'price', // Forzar que vaya en el panel principal del precio
        figures: [
            { key: 'sma', title: 'SMA 10: ', type: 'line' },
            { key: 'signal', title: 'Punto: ', type: 'circle' }
        ],
        calc: (dataList) => {
            const period = 10;
            return dataList.map((bar, i, arr) => {
                if (i < period) return { sma: null, signal: null };
                
                let sum = 0;
                for (let j = i - period; j <= i; j++) {
                    sum += arr[j].close;
                }
                let valSma = sum / period;
                
                // Ponemos un punto de señal cada 15 velas para comprobar que se dibujan
                let sig = (i % 15 === 0) ? bar.high + 0.0020 : null;
                
                return {
                    sma: valSma,
                    signal: sig
                };
            });
        },
        styles: {
            lines: [{ color: '#ffea00', size: 2 }],
            circles: [{ color: '#00e676', radius: 7 }]
        }
    });
    chart.createIndicator("AVIZOR_SIMPLE_TEST");
}"""
    
    code_input = st.text_area("Código del indicador:", value=default_code, height=420)
    
    if st.button("🚀 Cargar Indicador en Gráfico", type="primary", use_container_width=True):
        st.session_state.render_trigger = True
        st.success("¡Indicador de prueba enviado!")

with col_chart:
    st.subheader("📊 Visualizador Principal EURUSD")
    compiled_code = engine.parse_to_klinechart(selected_mode, code_input)
    chart_html = get_chart_html(compiled_code)
    components.html(chart_html, height=740)
