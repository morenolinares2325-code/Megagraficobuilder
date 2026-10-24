# klinechart/renderer.py (o dentro de una estructura limpia)

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
            
            // Datos de prueba (velas OHLCV simuladas para NVDA/Testing)
            const mockData = [
                {{ timestamp: 1710000000000, open: 210, high: 215, low: 208, close: 213, volume: 1500 }},
                {{ timestamp: 1710086400000, open: 213, high: 218, low: 212, close: 216, volume: 1800 }},
                {{ timestamp: 1710172800000, open: 216, high: 220, low: 214, close: 219, volume: 2200 }},
                {{ timestamp: 1710259200000, open: 219, high: 222, low: 217, close: 218, volume: 1600 }},
                {{ timestamp: 1710345600000, open: 218, high: 225, low: 218, close: 224, volume: 2500 }}
            ];
            chart.applyNewData(mockData);

            // Inyección segura del script del indicador del Builder
            try {{
                {indicator_script}
            }} catch (e) {{
                console.error("Error al registrar el indicador:", e);
            }}
        </script>
    </body>
    </html>
    """
