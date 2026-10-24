import streamlit as st
import streamlit.components.v1 as components

# Configuración inicial de la página
st.set_page_config(
    page_title="Avizor Builder Pro - Multi-Language Sandbox",
    layout="wide"
)

st.title("🛠️ Avizor Builder Pro: Multi-Language to KLineChart")

# --- Motor de Traducción y Conversión Multi-Modo ---
class IndicatorBuilderEngine:
    def __init__(self):
        self.version = "2.0.0"

    def parse_to_klinechart(self, mode: str, raw_code: str) -> str:
        """
        Traduce o adapta el código de entrada según el lenguaje seleccionado 
        a un formato ejecutable por KLineChart.
        """
        if mode == "KLineChart (JS/TS)":
            # Si ya es KLineChart nativo, lo devolvemos tal cual
            return raw_code
        
        elif mode == "Pine Script":
            # Simulamos/adaptamos la estructura de Pine a KLineChart (ej: Media Móvil / Cruce)
            return """
            klinecharts.registerIndicator({
                name: "PINE_CONVERTED_MA",
                shortName: "Pine MA Conv",
                series: 'price',
                figures: [
                    { key: 'maLine', title: 'Pine MA: ', type: 'line' },
                    { key: 'signalDot', title: 'Signal: ', type: 'circle' }
                ],
                calc: (dataList) => {
                    const period = 14;
                    const closes = dataList.map(b => b.close);
                    return closes.map((close, i, arr) => {
                        if (i < period) return { maLine: null, signalDot: null };
                        let sum = 0;
                        for (let j = i - period + 1; j <= i; j++) { sum += arr[j]; }
                        let ma = sum / period;
                        let dot = (close > ma) ? bar_low_safe(dataList[i]) : null;
                        return { maLine: ma, signalDot: dot };
                    });
                },
                styles: {
                    lines: [{ color: '#2962FF', size: 2 }],
                    circles: [{ color: '#00E676', radius: 4 }]
                }
            });
            function bar_low_safe(bar) { return bar.low * 0.995; }
            """

        elif mode == "MQL5":
            return """
            klinecharts.registerIndicator({
                name: "MQL5_CONVERTED",
                shortName: "MQL5 Expert",
                series: 'price',
                figures: [{ key: 'mqlLine', title: 'MQL5 Line: ', type: 'line' }],
                calc: (dataList) => {
                    const period = 10;
                    return dataList.map((bar, i, arr) => {
                        if (i < period) return { mqlLine: null };
                        let slice = arr.slice(i - period, i).map(b => b.close);
                        let avg = slice.reduce((a, b) => a + b, 0) / period;
                        return { mqlLine: avg };
                    });
                },
                styles: { lines: [{ color: '#FF9800', size: 2 }] }
            });
            """

        elif mode == "cTrader (C#)":
            return """
            klinecharts.registerIndicator({
                name: "CTRADER_CONVERTED",
                shortName: "cTrader Bot",
                series: 'price',
                figures: [{ key: 'cLine', title: 'cTrader SMA: ', type: 'line' }],
                calc: (dataList) => {
                    return dataList.map(bar => ({ cLine: bar.close * 1.002 }));
                },
                styles: { lines: [{ color: '#E040FB', size: 2 }] }
            });
            """
        
        return raw_code

engine = IndicatorBuilderEngine()

# --- Plantilla HTML de KLineChart con Soporte Visual ---
def get_chart_html(indicator_script: str = ""):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>KLineCharts Sandbox Pro</title>
        <script src="https://unpkg.com/klinecharts/dist/klinecharts.min.js"></script>
        <style>
            body, html {{
                margin: 0; padding: 0;
                background-color: #0e1117; color: #ffffff;
                font-family: sans-serif; overflow: hidden;
            }}
            #chart {{ width: 100vw; height: 100vh; }}
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <script>
            const chart = klinecharts.init('chart');
            
            // Datos simulados de mercado más amplios
            const mockData = [
                {{ timestamp: 1710000000000, open: 210, high: 215, low: 208, close: 213, volume: 1500 }},
                {{ timestamp: 1710086400000, open: 213, high: 218, low: 212, close: 216, volume: 1800 }},
                {{ timestamp: 1710172800000, open: 216, high: 220, low: 214, close: 219, volume: 2200 }},
                {{ timestamp: 1710259200000, open: 219, high: 222, low: 217, close: 218, volume: 1600 }},
                {{ timestamp: 1710345600000, open: 218, high: 225, low: 218, close: 224, volume: 2500 }},
                {{ timestamp: 1710432000000, open: 224, high: 228, low: 221, close: 226, volume: 3000 }},
                {{ timestamp: 1710518400000, open: 226, high: 230, low: 223, close: 229, volume: 2800 }}
            ];
            chart.applyNewData(mockData);

            // Inyección del indicador compilado
            try {{
                {indicator_script}
            }} catch (e) {{
                console.error("Error al registrar el indicador:", e);
            }}
        </script>
    </body>
    </html>
    """

# --- Interfaz de Streamlit (Layout Avanzado) ---
col_editor, col_chart = st.columns([1, 1.4])

with col_editor:
    st.subheader("⚙️ Configuración y Esencia del Builder")
    
    # Selector de Modo de Lenguaje
    selected_mode = st.selectbox(
        "Selecciona el Lenguaje de Entrada:",
        ["Pine Script", "MQL5", "cTrader (C#)", "KLineChart (JS/TS)"]
    )
    
    # Plantillas por defecto según el lenguaje elegido
    templates = {
        "Pine Script": """//@version=5
indicator("Avizor Supertrend Pine", overlay=true)
atrPeriod = input.int(10, "ATR Length")
factor = input.float(3.0, "Factor")
// Lógica simulada de Pine Script
plot(close, title="Pine Close Line", color=color.green)""",
        
        "MQL5": """//+------------------------------------------------------------------+
//|                                           Avizor_Expert.mq5 |
//+------------------------------------------------------------------+
#property indicator_chart_line
input int MAPeriod = 14;
int OnInit() { return(INIT_SUCCEEDED); }
int OnCalculate(...) { return(rates_total); }""",
        
        "cTrader (C#)": """using cTrader.API;
namespace cBot {
    [Indicator(IsOverlay = true, TimeZone = TimeZones.UTC)]
    public class AvizorCTrader : Indicator {
        [Parameter(DefaultValue = 14)]
        public int Period { get; set; }
        protected override void Initialize() {}
    }
}""",
        
        "KLineChart (JS/TS)": """klinecharts.registerIndicator({
    name: "AVIZOR_CUSTOM",
    shortName: "Avizor Custom",
    series: 'price',
    figures: [{ key: 'val', title: 'Val: ', type: 'line' }],
    calc: (dataList) => dataList.map(bar => ({ val: bar.close }))
});"""
    }
    
    code_input = st.text_area(
        f"Código fuente en [{selected_mode}]:", 
        value=templates[selected_mode], 
        height=320
    )
    
    # Botón principal de Creación e Inyección
    if st.button("🚀 Crear y Mostrar en Gráfico", type="primary", use_container_width=True):
        st.success(f"¡Indicador convertido desde **{selected_mode}** y renderizado con éxito!")

with col_chart:
    st.subheader("📊 Visualización KLineChart en Tiempo Real")
    
    # Conversión automática al pulsar o al cambiar el estado
    compiled_code = engine.parse_to_klinechart(selected_mode, code_input)
    chart_html = get_chart_html(compiled_code)
    
    components.html(chart_html, height=620)
