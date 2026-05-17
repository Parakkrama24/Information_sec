from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os
import json
import threading
import time
import signal

app = Flask(__name__)
CORS(app)

# Global variables
server_process = None
server_logs = []
vehicle_logs = []
telemetry_data = None
base_dir = os.path.dirname(os.path.abspath(__file__))

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# Get folder structure
@app.route('/api/folder-structure', methods=['GET'])
def get_folder_structure():
    def build_tree(path, max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return {}

        tree = {}
        try:
            items = os.listdir(path)
            for item in sorted(items):
                item_path = os.path.join(path, item)

                # Skip hidden files and common directories to ignore
                if item.startswith('.') or item in ['__pycache__', 'venv', 'node_modules']:
                    continue

                if os.path.isdir(item_path):
                    tree[item] = build_tree(item_path, max_depth, current_depth + 1)
                else:
                    tree[item] = None
        except PermissionError:
            pass

        return tree

    structure = build_tree(base_dir)
    return jsonify({'structure': structure}), 200

# Start edge server
@app.route('/api/start-server', methods=['POST'])
def start_server():
    global server_process, server_logs

    if server_process and server_process.poll() is None:
        return jsonify({'success': False, 'message': 'Server already running'}), 400

    try:
        server_logs = []
        server_process = subprocess.Popen(
            ['python', 'edge_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=base_dir,
            bufsize=1
        )

        # Give server time to start
        time.sleep(1)

        if server_process.poll() is not None:
            stderr = server_process.stderr.read()
            return jsonify({'success': False, 'message': f'Server failed to start: {stderr}'}), 500

        return jsonify({'success': True, 'message': 'Edge server started'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Stop edge server
@app.route('/api/stop-server', methods=['POST'])
def stop_server():
    global server_process, server_logs

    if server_process and server_process.poll() is None:
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
            server_logs = []
            return jsonify({'success': True, 'message': 'Server stopped'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    return jsonify({'success': False, 'message': 'Server not running'}), 400

# Run vehicle client
@app.route('/api/run-vehicle', methods=['POST'])
def run_vehicle():
    global vehicle_logs, server_logs, telemetry_data

    if not server_process or server_process.poll() is not None:
        return jsonify({'success': False, 'message': 'Edge server not running'}), 400

    try:
        vehicle_logs = []

        vehicle_process = subprocess.run(
            ['python', 'vehicle.py'],
            capture_output=True,
            text=True,
            cwd=base_dir,
            timeout=10
        )

        # Parse vehicle output
        vehicle_output = vehicle_process.stdout.strip().split('\n')
        vehicle_logs = [line for line in vehicle_output if line.strip()]

        # Give server time to process and read its output
        time.sleep(0.5)

        # Note: Reading server output in real-time is complex on Windows
        # The full test endpoint should be used instead for complete logs

        return jsonify({
            'success': True,
            'logs': vehicle_logs
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'message': 'Vehicle client timed out'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Run full test
@app.route('/api/run-full-test', methods=['POST'])
def run_full_test():
    global server_logs, vehicle_logs, telemetry_data

    try:
        server_logs = []
        vehicle_logs = []
        telemetry_data = None

        # Run the test script
        test_process = subprocess.run(
            ['python', 'test_system.py'],
            capture_output=True,
            text=True,
            cwd=base_dir,
            timeout=30
        )

        output = test_process.stdout

        # Parse output to separate server and vehicle logs
        lines = output.split('\n')

        in_vehicle_section = False
        in_server_section = False

        for line in lines:
            line = line.strip()
            if not line or '=' in line:
                continue

            if '--- Vehicle Client Output ---' in line:
                in_vehicle_section = True
                in_server_section = False
                continue
            elif '--- Edge Server Output ---' in line:
                in_vehicle_section = False
                in_server_section = True
                continue

            if in_vehicle_section and line:
                vehicle_logs.append(line)
            elif in_server_section and line:
                server_logs.append(line)

        # Try to extract telemetry from server logs
        try:
            in_json = False
            json_lines = []
            for line in server_logs:
                if '{' in line:
                    in_json = True
                if in_json:
                    json_lines.append(line)
                if '}' in line and in_json:
                    break

            if json_lines:
                json_str = '\n'.join(json_lines)
                telemetry_data = json.loads(json_str)
        except:
            pass

        return jsonify({
            'success': True,
            'server_logs': server_logs,
            'vehicle_logs': vehicle_logs,
            'telemetry': telemetry_data
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Get server logs
@app.route('/api/server-logs', methods=['GET'])
def get_server_logs():
    return jsonify({'logs': server_logs}), 200

# Get telemetry data
@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    return jsonify({'telemetry': telemetry_data}), 200

if __name__ == '__main__':
    print("Starting API Server...")
    print("API Server running on http://localhost:5000")
    print("Open UI/index.html in your browser to access the dashboard")

    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        if server_process and server_process.poll() is None:
            server_process.terminate()
        print("\nAPI Server stopped")
