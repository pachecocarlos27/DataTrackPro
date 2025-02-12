"""
Web dashboard module for real-time monitoring of pipeline metrics.
"""
from .app import app, socketio, emit_metric

__all__ = ['app', 'socketio', 'emit_metric']