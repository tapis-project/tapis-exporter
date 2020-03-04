from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/metrics')
def metrics():
    return "Here there be metrics."