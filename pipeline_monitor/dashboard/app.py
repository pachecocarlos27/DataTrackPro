from flask import Flask, render_template
from flask_socketio import SocketIO
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Initialize Flask-SocketIO
socketio = SocketIO()

def create_dashboard_app() -> Flask:
    """
    Create and configure the Flask application for the monitoring dashboard.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'pipeline-monitor-secret'  # For development only
    
    # Initialize SocketIO with the app
    socketio.init_app(app)
    
    @app.route('/')
    def dashboard():
        """Render the main dashboard page."""
        return render_template('dashboard.html')
    
    @socketio.on('connect')
    def handle_connect():
        """Handle WebSocket connection."""
        logger.info("Client connected to dashboard")
    
    return app

def emit_metric(metric_type: str, data: dict) -> None:
    """
    Emit a metric update to connected clients.
    
    Args:
        metric_type: Type of metric (e.g., 'performance', 'memory', 'alert')
        data: Metric data to emit
    """
    try:
        socketio.emit('metric_update', {
            'type': metric_type,
            'data': data
        })
    except Exception as e:
        logger.error(f"Failed to emit metric: {str(e)}")

def start_dashboard(host: str = '0.0.0.0', port: int = 5000, debug: bool = False) -> None:
    """
    Start the dashboard server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    app = create_dashboard_app()
    socketio.run(app, host=host, port=port, debug=debug)
