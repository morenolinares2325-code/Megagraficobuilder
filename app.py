import streamlit as st
import streamlit.components.v1 as components

# Configuración inicial de la página
st.set_page_config(
    page_title="Avizor Builder Sandbox",
    layout="wide"
)

st.title("🛠️ Avizor Builder & KLineChart Sandbox")

# --- Motor / Lógica del Builder (Integrado) ---
class IndicatorBuilderEngine:
    def __init__(self):
        self.version = "1.0.0"

    def parse_script(self, raw_code: str) -> str:
        """
        Aquí procesamos el código introducido para inyectarlo en el gráfico.
        """
        return raw_code

engine = IndicatorBuilderEngine()

# --- Plantilla HTML de KLineChart ---
def get_chart_html(indicator_script: str = ""):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>KLineCharts Sandbox</title>
        <!-- CDN oficial de KLineCharts -->
        <script src="https://unpkg.com/klinecharts/dist/klinecharts.min.js"></script>
        <style>
            body, html {{
                margin: 0;
                padding: 0;
                background-color: #121212;
                color: #ffffff;
                font-family: sans-serif;
                overflow: hidden;
            }}
            #chart {{
                width: 100vw;
                height: 100vh;
            }}
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <script>
            // Inicializar el gráfico
            const chart = klinecharts.init('chart');
            
            // Datos de prueba (velas OHLCV simuladas)
            const mockData = [
                {{ timestamp: 1710000000000, open: 210, high: 215, low: 208, close: 213, volume: 1500 }},
                {{ timestamp: 1710086400000, open: 213, high: 218, low: 212, close: 216, volume: 1800 }},
                {{ timestamp: 1710172800000, open: 216, high: 220, low: 214, close: 219, volume: 2200 }},
                {{ timestamp: 1710259200000, open: 219, high: 222, low: 217, close: 218, volume: 1600 }},
                {{ timestamp: 1710345600000, open: 218, high: 225, low: 218, close: 224, volume: 2500 }}
            ];
            chart.applyNewData(mockData);

            // Inyección segura del script del indicador
            try {{
                {indicator_script}
            }} catch (e) {{
                console.error("Error al registrar el indicador:", e);
            }}
        </script>
    </body>
    </html>
    """

# --- Interfaz de Streamlit (Layout de dos columnas) ---
col_editor, col_chart = st.columns([1, 1.5])

with col_editor:
    st.subheader("Editor de Indicadores")
    
    default_code = """// Ejemplo de registro directo en KLineChart
klinecharts.registerIndicator({
    name: "TEST_DOT",
    shortName: "Test Dot",
    series: 'price',
    figures: [{ key: 'value', title: 'Val: ', type: 'line' }],
    calc: (dataList) => {
        return dataList.map(bar => ({ value: bar.close }));
    }
});"""
    
    code_input = st.text_area("Código del Indicador (JS/TS):", value=default_code, height=400)
    
    if st.button("🚀 Compilar y Renderizar"):
        st.success(f"Motor v{engine.version}: ¡Código procesado con éxito!")

with col_chart:
    st.subheader("Visualización en Tiempo Real")
    # Procesamos y renderizamos el gráfico con el código actual
    compiled_code = engine.parse_script(code_input)
    chart_html = get_chart_html(compiled_code)
    components.html(chart_html, height=600)
