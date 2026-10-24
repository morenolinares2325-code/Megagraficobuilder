import sys
import os
import streamlit as st
from klinechart.renderer import get_chart_html
from builder.parser import IndicatorBuilderEngine
import streamlit.components.v1 as components

st.set_page_config(page_title="Avizor Builder Sandbox", layout="wide")

# Inicializamos el motor del builder
engine = IndicatorBuilderEngine()

st.title("🛠️ Avizor Builder & KLineChart Sandbox")

col_editor, col_chart = st.columns([1, 1.5])

with col_editor:
    st.subheader("Editor de Indicadores")
    default_code = """
    // Ejemplo de registro directo en KLineChart
    klinecharts.registerIndicator({
        name: "TEST_DOT",
        shortName: "Test Dot",
        series: 'price',
        figures: [{ key: 'value', title: 'Val: ', type: 'line' }],
        calc: (dataList) => {
            return dataList.map(bar => ({ value: bar.close }));
        }
    });
    """
    code_input = st.text_area("Código del Indicador (JS/TS):", value=default_code, height=400)
    
    if st.button("🚀 Compilar y Renderizar"):
        st.success(f"Motor v{engine.version}: ¡Código procesado!")

with col_chart:
    st.subheader("Visualización en Tiempo Real")
    # Procesamos a través del motor del builder
    compiled_code = engine.parse_script(code_input)
    chart_html = get_chart_html(compiled_code)
    components.html(chart_html, height=600)
