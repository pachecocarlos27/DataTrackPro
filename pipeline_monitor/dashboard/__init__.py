"""
Web dashboard module for real-time monitoring of pipeline metrics.
"""
from flask import Flask
from flask_socketio import SocketIO
from .app import app, socketio, emit_metric, start_dashboard

__all__ = ['app', 'socketio', 'emit_metric', 'start_dashboard']

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return "Datant Pipeline Monitor Dashboard"