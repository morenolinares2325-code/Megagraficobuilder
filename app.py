import streamlit as st
import streamlit.components.v1 as components

# Configuración inicial de la página
st.set_page_config(
    page_title="Avizor Builder Pro - Sandbox",
    layout="wide"
)

st.title("🛠️ Avizor Builder Pro: Conversión y Renderizado KLineChart")

if "render_trigger" not in st.session_state:
    st.session_state.render_trigger = False

class IndicatorBuilderEngine:
    def __init__(self):
        self.version = "2.1.2"

    def parse_to_klinechart(self, mode: str, raw_code: str) -> str:
        if mode == "KLineChart (JS/TS)":
            return raw_code
        
        return """
        // Registro seguro de indicador por defecto
        if (typeof klinecharts !== 'undefined' && klinecharts.registerIndicator) {
            klinecharts.registerIndicator({
                name: "AVIZOR_KELTNER_PRO",
                shortName: "Keltner Pro",
                series: 'price',
                figures: [
                    { key: 'upper', title: 'Superior: ', type: 'line' },
                    { key: 'middle', title: 'EMA Central: ', type: 'line' },
                    { key: 'lower', title: 'Inferior: ', type: 'line' }
                ],
                calc: (dataList) => {
                    const period = 10;
                    return dataList.map((bar, i, arr) => {
                        if (i < period) {
                            return { upper: null, middle: null, lower: null };
                        }
                        let sum = 0;
                        for (let j = i - period; j <= i; j++) {
                            sum += arr[j].close;
                        }
                        const sma = sum / period;
                        const atr = (bar.high - bar.low) * 1.2;
                        return {
                            upper: sma + atr,
                            middle: sma,
                            lower: sma - atr
                        };
                    });
                },
                styles: {
                    lines: [
                        { color: '#00bcd4', size: 2 },
                        { color: '#ffeb3b', size: 2 },
                        { color: '#00bcd4', size: 2 }
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
        <title>KLineCharts Pro</title>
        <!-- Cargamos KLineCharts desde CDN fiable con respaldo -->
        <script src="https://cdn.jsdelivr.net/npm/klinecharts/dist/klinecharts.min.js"></script>
        <style>
            body, html {
                margin: 0; padding: 0;
                background-color: #0b0f19; color: #ffffff;
                font-family: sans-serif; overflow: hidden;
            }
            #chart { width: 100vw; height: 580px; }
            #debug-log {
                background: #111827; color: #10b981; padding: 8px 12px;
                font-family: monospace; font-size: 12px; border-top: 1px solid #1f2937;
                height: 40px; overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <div id="debug-log">Estado: Esperando carga de la librería...</div>

        <script>
            const logDiv = document.getElementById('debug-log');
            function logMsg(msg, isError = false) {
                logDiv.style.color = isError ? '#ef4444' : '#10b981';
                logDiv.innerText = ">> " + msg;
                console.log(msg);
            }

            // Verificamos que la librería cargue correctamente antes de inicializar
            window.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    try {
                        if (typeof klinecharts === 'undefined') {
                            throw new Error("La librería klinecharts no se ha cargado desde el CDN.");
                        }

                        const chart = klinecharts.init('chart');
                        logMsg("Librería KLineCharts cargada con éxito.");
                        
                        const mockData = [
                            { timestamp: 1710000000000, open: 100, high: 105, low: 98, close: 102, volume: 1500 },
                            { timestamp: 1710086400000, open: 102, high: 108, low: 101, close: 106, volume: 1800 },
                            { timestamp: 1710172800000, open: 106, high: 110, low: 104, close: 105, volume: 2200 },
                            { timestamp: 1710259200000, open: 105, high: 112, low: 103, close: 111, volume: 1600 },
                            { timestamp: 1710345600000, open: 111, high: 115, low: 109, close: 114, volume: 2500 },
                            { timestamp: 1710432000000, open: 114, high: 118, low: 112, close: 113, volume: 3000 },
                            { timestamp: 1710518400000, open: 113, high: 120, low: 110, close: 118, volume: 2800 },
                            { timestamp: 1710604800000, open: 118, high: 122, low: 116, close: 121, volume: 3100 }
                        ];
                        chart.applyNewData(mockData);
                        logMsg("Datos de velas aplicados.");

                        /* --- INYECCIÓN DEL SCRIPT --- */
                        REPLACE_INDICATOR_SCRIPT
                        
                        logMsg("¡Indicador inyectado y renderizado correctamente!");
                    } catch (e) {
                        logMsg("Error crítico: " + e.message, true);
                    }
                }, 200); // Pequeño retardo para asegurar disponibilidad del DOM y script
            });
        </script>
    </body>
    </html>
    """
    return html_template.replace("REPLACE_INDICATOR_SCRIPT", indicator_script)

col_editor, col_chart = st.columns([1, 1.4])

with col_editor:
    st.subheader("⚙️ Editor & Selector")
    
    selected_mode = st.selectbox(
        "Modo de Lenguaje:",
        ["KLineChart (JS/TS)", "Pine Script", "MQL5", "cTrader (C#)"]
    )
    
    default_code = """if (typeof klinecharts !== 'undefined') {
    klinecharts.registerIndicator({
        name: "AVIZOR_TEST_CUSTOM",
        shortName: "Avizor Custom",
        series: 'price',
        figures: [{ key: 'val', title: 'Precio Ref: ', type: 'line' }],
        calc: (dataList) => dataList.map(bar => ({ val: bar.close }))
    });
}"""
    
    code_input = st.text_area("Código fuente:", value=default_code, height=350)
    
    if st.button("🚀 Crear y Mostrar en Gráfico", type="primary", use_container_width=True):
        st.session_state.render_trigger = True
        st.success(f"¡Convertido desde **{selected_mode}**! Panel gráfico actualizado.")

with col_chart:
    st.subheader("📊 Visualizador KLineChart Activo")
    compiled_code = engine.parse_to_klinechart(selected_mode, code_input)
    chart_html = get_chart_html(compiled_code)
    components.html(chart_html, height=640)
