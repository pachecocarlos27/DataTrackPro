"""
Web dashboard module for real-time monitoring of pipeline metrics.
"""
from .app import app, socketio, emit_metric, start_dashboard

__all__ = ['app', 'socketio', 'emit_metric', 'start_dashboard']