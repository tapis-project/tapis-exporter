from app import app
import json
import requests

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

def get_health():
    r = requests.get('https://dev.develop.tapis.io/v3/security/ready')
    status = r.status_code
    message = json.loads(r.text)['message']
    if (status == 200) and ('TAPIS_READY' in message):
        return '0' # Healthy
    else:
        return '1' # Warning or Error

@app.route('/metrics')
def metrics():
    return get_health()