#!/usr/bin/env python3
"""Command-line interface for Pipeline Monitor."""

import sys
import json
from pipeline_monitor.dashboard import app, socketio
from pipeline_monitor.alerts import setup_alerts, log_alert_handler, email_alert_handler, slack_alert_handler, sms_alert_handler
from pipeline_monitor.config import Configuration

def load_config(config_path: str = None) -> Configuration:
    """Load configuration from file or create default."""
    if config_path:
        return Configuration.from_file(config_path)
    return Configuration()

def run_dashboard():
    """Entry point for the dashboard command"""
    print("Starting Pipeline Monitor Dashboard...")

def run_demo():
    """Entry point for the demo command"""
    print("Running Pipeline Monitor Demo...")

def run_prometheus():
    """Entry point for the prometheus command"""
    print("Starting Prometheus Integration...")

def test_alerts():
    """Entry point for testing alerts"""
    print("Testing Pipeline Monitor Alerts...")

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
        'pipeline-test-alerts': lambda: test_alerts()
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
