from typing import Any
from mcp.server.fastmcp import FastMCP
from loguru import logger
import json
from enum import Enum
from pathlib import Path
# Initialize FastMCP server
mcp = FastMCP(name="mcp_observability_server")

# Datasource paths
cwd = Path(__file__).parent.resolve()
DATASOURCE_PATH = cwd / "datasources"
LOGS_FOLDER = DATASOURCE_PATH / "logs"
LOGS = {
    "gateway": DATASOURCE_PATH / "logs/gateway.log",
    "notifications": DATASOURCE_PATH / "logs/notifications.log",
    "payments": DATASOURCE_PATH / "logs/payments.log",
}
ALERTS = DATASOURCE_PATH / "alerts.json"
INCIDENTS = DATASOURCE_PATH / "incidents.json"
METRICS = DATASOURCE_PATH / "metrics.json"
EVENTS = DATASOURCE_PATH / "events.json"

# ENUMs
class AppName(str, Enum):
    PAYMENTS = "payments"
    GATEWAY = "gateway"
    NOTIFICATIONS = "notifications"

# LOGS
@mcp.tool(name="get_info_logs", description="get all info logs")
def get_info_logs(appName: AppName | None = None):
    res = []
    if appName:
        appName = appName.value.lower()
        with open(file=LOGS[appName], mode="r") as log_file:
            lines = log_file.readlines()
            
            for line in lines:
                if "info" in line.lower():
                    res.append(line)
        return res
    
    for log in LOGS:
        with open(file=log, mode="r") as log_file:
            lines = log_file.readlines()
            
            for line in lines:
                if appName and appName.value.lower() not in log.lower():
                    continue
                if "info" in line.lower():
                    res.append(line)
    return res

@mcp.tool(name="get_error_logs", description="get all error logs")
def get_error_logs(appName: AppName | None = None):
    res = []
    if appName:
        appName = appName.value.lower()
        with open(file=LOGS[appName], mode="r") as log_file:
            lines = log_file.readlines()
            
            for line in lines:
                if "error" in line.lower():
                    res.append(line)
        return res
    
    for log in LOGS:
        with open(file=log, mode="r") as log_file:
            lines = log_file.readlines()
            
            for line in lines:
                if "error" in line.lower():
                    res.append(line)
    return res

# ALERTS
@mcp.tool(name="get_warning_alerts", description="get all warning alerts")
def get_warning_alerts(appName: AppName | None = None):
    res = []
    with open(file=ALERTS, mode="r") as alert_file:
        alerts = json.load(alert_file)
        
        for alert in alerts:
            if appName and alert["application"].lower() != appName.value.lower():
                continue
            if alert["severity"].lower() == "warning":
                res.append(alert)
    return res

@mcp.tool(name="get_critical_alerts", description="get all critical alerts")
def get_critical_alerts(appName: AppName | None = None):
    res = []
    with open(file=ALERTS, mode="r") as alert_file:
        alerts = json.load(alert_file)
        
        for alert in alerts:
            if appName and alert["application"].lower() != appName.value.lower():
                continue
            if alert["severity"].lower() == "critical":
                res.append(alert)
    return res

# INCIDENTS
@mcp.tool(name="get_unresolved_incidents", description="get all unresolved incidents")
def get_unresolved_incidents(appName: AppName | None = None):
    with open(file=INCIDENTS, mode="r") as incident_file:
        incidents = json.load(incident_file)
        unresolved = []
        for incident in incidents:
            if appName and incident["application"].lower() != appName.value.lower():
                continue
            if incident["resolved"] == False:
                unresolved.append(incident)
        return unresolved
    
@mcp.tool(name="get_resolved_incidents", description="get all resolved incidents")
def get_resolved_incidents(appName: AppName | None = None):
    with open(file=INCIDENTS, mode="r") as incident_file:
        incidents = json.load(incident_file)
        resolved = []
        for incident in incidents:
            if appName and incident["application"].lower() != appName.value.lower():
                continue
            if incident["resolved"]:
                resolved.append(incident)
        return resolved

@mcp.tool(name="get_metrics", description="get metrics")
def get_metrics(appName: AppName | None = None):
    with open(file=METRICS, mode="r") as metrics_file:
        metrics = json.load(metrics_file)
        res = []
        for metric in metrics:
            if appName and metric["application"].lower() != appName.value.lower():
                continue
            res.append(metric)
        return res

@mcp.tool(name="get_events", description="get events")
def get_events(app_name: AppName):
    with open(file=EVENTS, mode="r") as event_file:
        events = json.load(event_file)
        res = []
        for event in events:
            if event["application"].lower() == app_name.value.lower():
                res.append(event)
        return res

if __name__ == "__main__":
    mcp.run(transport='stdio')
