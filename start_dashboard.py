#!/usr/bin/env python3
"""
Launcher script for the Secure V2I Communication Dashboard
"""
import subprocess
import webbrowser
import time
import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("Secure V2I Communication Dashboard Launcher")
    print("=" * 60)
    print()

    # Get the directory where this script is located
    base_dir = Path(__file__).parent.absolute()
    ui_path = base_dir / "UI" / "index.html"

    # Check if required files exist
    if not (base_dir / "api_server.py").exists():
        print("ERROR: api_server.py not found!")
        sys.exit(1)

    if not ui_path.exists():
        print("ERROR: UI/index.html not found!")
        sys.exit(1)

    print("[1/2] Starting API Server...")
    print()

    # Start the API server in a subprocess
    try:
        server_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            cwd=base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for server to start
        print("Waiting for server to initialize...")
        time.sleep(3)

        # Check if server is still running
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print("ERROR: API Server failed to start!")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            sys.exit(1)

        print("[SUCCESS] API Server started on http://localhost:5000")
        print()

        print("[2/2] Opening dashboard in browser...")
        print()

        # Open the dashboard in the default browser
        webbrowser.open(ui_path.as_uri())

        print("=" * 60)
        print("Dashboard is now running!")
        print("=" * 60)
        print()
        print("API Server: http://localhost:5000")
        print(f"Dashboard: {ui_path}")
        print()
        print("Press Ctrl+C to stop the server and exit")
        print("=" * 60)
        print()

        # Keep the script running
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            server_process.terminate()
            server_process.wait(timeout=5)
            print("Server stopped. Goodbye!")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
