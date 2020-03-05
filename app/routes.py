from app import app

@app.route('/')
@app.route('/index')
def index():
    return """<!DOCTYPE html>
<html>
        <head><title>Tapis Exporter</title></head>
        <body>
                <h1>Tapis Exporter</h1>
                <p><a href='/metrics'>Metrics</a></p>
        </body>
</html>"""

@app.route('/metrics')
def metrics():
    return "Here there be metrics."