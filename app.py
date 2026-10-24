import streamlit as st
import streamlit.components.v1 as components

# Configuración inicial de la página
st.set_page_config(
    page_title="Avizor Builder Pro - Advanced Sandbox",
    layout="wide"
)

st.title("🛠️ Avizor Builder Pro: Entorno de Gráficos & Indicadores Pro")

if "render_trigger" not in st.session_state:
    st.session_state.render_trigger = False

class IndicatorBuilderEngine:
    def __init__(self):
        self.version = "2.3.0"

    def parse_to_klinechart(self, mode: str, raw_code: str) -> str:
        if mode == "KLineChart (JS/TS)":
            return raw_code
        
        # Plantilla del Canal Keltner optimizada para un histórico amplio
        return """
        if (typeof klinecharts !== 'undefined') {
            klinecharts.registerIndicator({
                name: "AVIZOR_KELTNER_PRO",
                shortName: "Keltner Channel Pro",
                series: 'price',
                figures: [
                    { key: 'upper', title: 'Banda Sup: ', type: 'line' },
                    { key: 'middle', title: 'EMA Central: ', type: 'line' },
                    { key: 'lower', title: 'Banda Inf: ', type: 'line' }
                ],
                calc: (dataList) => {
                    const period = 20;
                    return dataList.map((bar, i, arr) => {
                        if (i < period) {
                            return { upper: null, middle: null, lower: null };
                        }
                        let sum = 0;
                        for (let j = i - period; j <= i; j++) {
                            sum += arr[j].close;
                        }
                        const sma = sum / period;
                        const atr = (bar.high - bar.low) * 1.5;
                        return {
                            upper: sma + atr,
                            middle: sma,
                            lower: sma - atr
                        };
                    });
                },
                styles: {
                    lines: [
                        { color: '#00e5ff', size: 1.5 }, // Banda Superior Cyan
                        { color: '#ffea00', size: 2 },     // EMA Central Amarillo
                        { color: '#00e5ff', size: 1.5 }     // Banda Inferior Cyan
                    ]
                }
            });
        }
        """

engine = IndicatorBuilderEngine()

def get_chart_html(indicator_script: str = ""):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>KLineCharts Pro Historical</title>
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
            <span id="status-text">Estado: Generando histórico de 2 años...</span>
            <span id="candles-count">Velas: 0</span>
        </div>

        <script>
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

                        const chart = klinecharts.init('chart', {
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
                        
                        setStatus("Construyendo histórico masivo (Diario)...");

                        // Generación de un histórico de ~500 velas diarias (aprox. 2 años de bolsa)
                        let baseTime = Date.now() - (500 * 24 * 60 * 60 * 1000); 
                        let basePrice = 100.0;
                        let mockData = [];

                        for (let i = 0; i < 500; i++) {
                            let trend = Math.sin(i / 30) * 2.5; // Olas de mercado realistas
                            let variation = (Math.random() - 0.49) * 4.0 + trend;
                            let open = basePrice;
                            let close = open + variation;
                            let high = Math.max(open, close) + Math.random() * 2.5;
                            let low = Math.min(open, close) - Math.random() * 2.5;
                            let volume = Math.floor(Math.random() * 80000) + 15000;

                            // Evitar precios negativos
                            if (low < 5) low = 5;

                            mockData.push({
                                timestamp: baseTime + (i * 24 * 60 * 60 * 1000), // un día por vela
                                open: parseFloat(open.toFixed(2)),
                                high: parseFloat(high.toFixed(2)),
                                low: parseFloat(low.toFixed(2)),
                                close: parseFloat(close.toFixed(2)),
                                volume: volume
                            });
                            basePrice = close;
                        }

                        chart.applyNewData(mockData);
                        candlesCount.innerText = "Velas: " + mockData.length + " (2 Años)";
                        setStatus("Histórico masivo aplicado.");

                        /* --- INYECCIÓN DEL SCRIPT DEL INDICADOR --- */
                        REPLACE_INDICATOR_SCRIPT
                        
                        setStatus("¡Indicador Keltner Pro aplicado sobre 2 años de histórico!");
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
    st.subheader("⚙️ Editor de Estrategia & Builder")
    
    selected_mode = st.selectbox(
        "Modo de Lenguaje:",
        ["KLineChart (JS/TS)", "Pine Script", "MQL5", "cTrader (C#)"]
    )
    
    # Ponemos por defecto el código del Canal Keltner que querías probar
    default_code = """if (typeof klinecharts !== 'undefined') {
    klinecharts.registerIndicator({
        name: "AVIZOR_KELTNER_PRO",
        shortName: "Keltner Channel Pro",
        series: 'price',
        figures: [
            { key: 'upper', title: 'Banda Sup: ', type: 'line' },
            { key: 'middle', title: 'EMA Central: ', type: 'line' },
            { key: 'lower', title: 'Banda Inf: ', type: 'line' }
        ],
        calc: (dataList) => {
            const period = 20;
            return dataList.map((bar, i, arr) => {
                if (i < period) return { upper: null, middle: null, lower: null };
                let sum = 0;
                for (let j = i - period; j <= i; j++) sum += arr[j].close;
                const sma = sum / period;
                const atr = (bar.high - bar.low) * 1.5;
                return { upper: sma + atr, middle: sma, lower: sma - atr };
            });
        },
        styles: {
            lines: [
                { color: '#00e5ff', size: 1.5 },
                { color: '#ffea00', size: 2 },
                { color: '#00e5ff', size: 1.5 }
            ]
        }
    });
}"""
    
    code_input = st.text_area("Código fuente del Indicador:", value=default_code, height=400)
    
    if st.button("🚀 Crear y Mostrar en Gráfico", type="primary", use_container_width=True):
        st.session_state.render_trigger = True
        st.success(f"¡Indicador compilado desde **{selected_mode}** y aplicado al histórico de 2 años!")

with col_chart:
    st.subheader("📊 Visualizador KLineChart Pro (Histórico Extendido)")
    compiled_code = engine.parse_to_klinechart(selected_mode, code_input)
    chart_html = get_chart_html(compiled_code)
    components.html(chart_html, height=740)
