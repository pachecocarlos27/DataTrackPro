from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import json
import logging
from typing import Optional
from prometheus_client import generate_latest
from ..prometheus_metrics import REGISTRY

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'pipeline-monitor-secret'

# Initialize Flask-SocketIO with async mode
socketio = SocketIO(app, async_mode='threading', logger=True, engineio_logger=True)

@app.route('/')
def dashboard():
    """Render the main dashboard page."""
    return render_template('dashboard.html')

@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info("Client connected to dashboard")

@socketio.on_error_default
def error_handler(e):
    """Handle WebSocket errors."""
    logger.error(f"WebSocket error: {str(e)}")

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

    # Send SMS alert if metric type is 'alert'
    if metric_type == 'alert':
        from ..alerts import sms_alert_handler
        from ..config import Configuration

        config = Configuration.from_file("examples/config.json")
        sms_cfg = config.get('alerts', {}).get('sms', {})
        if sms_cfg:
            handler = sms_alert_handler(
                provider_url=sms_cfg['provider_url'],
                api_key=sms_cfg['api_key'],
                sender_number=sms_cfg['sender_number'],
                recipient_numbers=sms_cfg['recipient_numbers']
            )
            alert_msg = data.get('message', 'No message provided')
            handler(alert_msg, data)

def start_dashboard(
    host: str = '0.0.0.0',
    port: int = 5000,
    debug: bool = False,
    use_reloader: bool = False
) -> None:
    """
    Start the monitoring dashboard server.

    Args:
        host: Host to bind to (default: '0.0.0.0')
        port: Port to listen on (default: 5000)
        debug: Enable debug mode
        use_reloader: Enable auto-reloader (default: False)
    """
    try:
        logger.info(f"Starting dashboard on {host}:{port}")
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=use_reloader,
            log_output=True
        )
    except Exception as e:
        logger.error(f"Failed to start dashboard: {str(e)}")
        raise
