"""
NIDS Flask Demo with Live Frontend Alerts

 - Shows both NORMAL (INFO) and ALERT messages on webpage.
 - Safe for demo without real packet sniffing.
 - Uses Flask with background thread for simulated sniffing output.
"""

from flask import Flask, render_template_string, jsonify
import threading
import time
import random

app = Flask(__name__)

# Shared storage for messages
alerts = []
stop_sniffing = False

# HTML Template (Live Page)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>NIDS Live Monitor</title>
    <style>
        body { background-color: #000; color: #0f0; font-family: Consolas, monospace; padding: 20px; }
        h2 { color: cyan; }
        .alert { color: red; }
        .info { color: #0f0; }
        #log { white-space: pre-wrap; background-color: #000; padding: 10px; border-radius: 8px; border: 1px solid #333; }
        button {
            background-color: cyan; color: black; padding: 8px 16px;
            font-weight: bold; border: none; border-radius: 8px; cursor: pointer;
        }
        button:hover { background-color: lime; }
    </style>
</head>
<body>
    <h2> Network Intrusion Detection System - Live Monitor</h2>
    <button onclick="startSniff()">Start Monitoring</button>
    <button onclick="stopSniff()">Stop</button>

    <h3>Live Alerts:</h3>
    <div id="log"></div>

    <script>
        let running = false;

        function updateLogs() {
            fetch('/alerts')
            .then(r => r.json())
            .then(data => {
                const logDiv = document.getElementById("log");
                logDiv.innerHTML = "";
                data.alerts.forEach(msg => {
                    if (msg.includes("ALERT")) {
                        logDiv.innerHTML += `<div class='alert'>${msg}</div>`;
                    } else {
                        logDiv.innerHTML += `<div class='info'>${msg}</div>`;
                    }
                });
            });
        }

        setInterval(updateLogs, 2000);

        function startSniff() {
            fetch('/start');
            running = true;
        }

        function stopSniff() {
            fetch('/stop');
            running = false;
        }
    </script>
</body>
</html>
"""

# Function to add message
def log_alert(message):
    alerts.append(message)
    if len(alerts) > 50:
        alerts.pop(0)

# Simulated sniffing thread
def simulate_sniffing():
    global stop_sniffing
    while not stop_sniffing:
        time.sleep(random.uniform(1, 3))

        # Randomly choose message type
        if random.random() < 0.3:
            msg = f"[{time.strftime('%H:%M:%S')}] ALERT: Suspicious activity detected from 192.168.1.{random.randint(2, 100)}"
        else:
            msg = f"[{time.strftime('%H:%M:%S')}] INFO: Normal traffic from 192.168.1.{random.randint(2, 100)}"
        log_alert(msg)

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/start")
def start_sniff():
    global stop_sniffing
    stop_sniffing = False
    threading.Thread(target=simulate_sniffing, daemon=True).start()
    return jsonify({"status": "started"})

@app.route("/stop")
def stop_sniff():
    global stop_sniffing
    stop_sniffing = True
    return jsonify({"status": "stopped"})

@app.route("/alerts")
def get_alerts():
    return jsonify({"alerts": alerts})

if __name__ == "__main__":
    print("[*] Starting Flask NIDS Demo Server on http://127.0.0.1:5000")
    app.run(debug=True)
