from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('https://linksb.me/')

def run_server():
    app.run('0.0.0.0', port=8080)