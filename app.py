import streamlit as st
from klinechart.renderer import get_chart_html
import streamlit.components.v1 as components

st.set_page_config(page_title="Avizor Builder Sandbox", layout="wide")

st.title("🛠️ Avizor Builder & KLineChart Sandbox")

# Layout de dos columnas
col_editor, col_chart = st.columns([1, 1.5])

with col_editor:
    st.subheader("Editor de Indicadores")
    default_code = """
    // Escribe o prueba tu código aquí
    console.log("KLineChart listo para recibir indicadores");
    """
    code_input = st.text_area("Código del Indicador (JS/TS):", value=default_code, height=400)
    
    if st.button("🚀 Compilar y Renderizar"):
        st.success("¡Código enviado al canvas!")

with col_chart:
    st.subheader("Visualización en Tiempo Real")
    # Renderizamos el componente HTML con el script introducido
    chart_html = get_chart_html(code_input)
    components.html(chart_html, height=600)
