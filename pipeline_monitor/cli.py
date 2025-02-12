#!/usr/bin/env python3
"""Command-line interface for Pipeline Monitor."""

import sys
from pipeline_monitor.dashboard import app, socketio

def run_dashboard():
    """Run the monitoring dashboard."""
    try:
        print("Starting Pipeline Monitor dashboard on http://0.0.0.0:5000")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)

def run_demo():
    """Run the basic monitoring demo."""
    try:
        from examples import dashboard_demo
        dashboard_demo.run_demo()
    except Exception as e:
        print(f"Error running demo: {e}")
        sys.exit(1)

def run_prometheus():
    """Run the Prometheus metrics demo."""
    try:
        from examples import prometheus_demo
        prometheus_demo.run_demo()
    except Exception as e:
        print(f"Error running Prometheus demo: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("Pipeline Monitor CLI")
    print("Available commands:")
    print("  pipeline-dashboard - Run the monitoring dashboard")
    print("  pipeline-demo - Run the basic monitoring demo")
    print("  pipeline-prometheus - Run the Prometheus metrics demo")
    sys.exit(1)