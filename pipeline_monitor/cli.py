#!/usr/bin/env python3
"""Command-line interface for Pipeline Monitor."""

import sys
import json
from pipeline_monitor.dashboard import app, socketio
from pipeline_monitor.alerts import setup_alerts, log_alert_handler, email_alert_handler, slack_alert_handler
from pipeline_monitor.config import Configuration

def load_config(config_path: str = None) -> Configuration:
    """Load configuration from file or create default."""
    if config_path:
        return Configuration.from_file(config_path)
    return Configuration()

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

def test_alerts(config_path: str = None):
    """
    Test the alerts system using configuration.
    
    Args:
        config_path: Optional path to configuration file
    """
    try:
        config = load_config(config_path)
        alert_config = config.get('alerts', {})
        
        # Set up appropriate handler based on configuration
        if alert_config.get('slack_webhook'):
            handler = slack_alert_handler(alert_config['slack_webhook'])
        elif alert_config.get('email'):
            email_cfg = alert_config['email']
            handler = email_alert_handler(
                smtp_host=email_cfg['smtp_host'],
                smtp_port=email_cfg['smtp_port'],
                sender=email_cfg['sender'],
                password=email_cfg['password'],
                recipients=email_cfg['recipients']
            )
        else:
            handler = log_alert_handler

        alert_hook = setup_alerts(handler)
        print("Testing alert system...")
        
        test_data = {
            "source": "CLI",
            "type": "test",
            "config": json.dumps(alert_config, default=str)
        }
        
        alert_hook.alert("Test alert from Pipeline Monitor", test_data)
        print("Alert sent successfully")
        
    except Exception as e:
        print(f"Error testing alerts: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else None

    commands = {
        'pipeline-dashboard': run_dashboard,
        'pipeline-demo': run_demo,
        'pipeline-prometheus': run_prometheus,
        'pipeline-test-alerts': lambda: test_alerts(config_path)
    }

    if command in commands:
        commands[command]()
    else:
        show_help()
        sys.exit(1)

def show_help():
    """Show CLI help message."""
    print("Pipeline Monitor CLI")
    print("Usage: pipeline-monitor <command> [config_path]")
    print("\nAvailable commands:")
    print("  pipeline-dashboard      - Run the monitoring dashboard")
    print("  pipeline-demo          - Run the basic monitoring demo")
    print("  pipeline-prometheus    - Run the Prometheus metrics demo")
    print("  pipeline-test-alerts   - Test the alerts system")
    print("\nOptions:")
    print("  config_path           - Optional path to configuration file")

if __name__ == '__main__':
    main()