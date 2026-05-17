import subprocess
import time
import sys

print("=" * 60)
print("Testing Secure V2I Communication System")
print("=" * 60)

# Start edge server in background
print("\n[1/2] Starting Edge Server...")
server_process = subprocess.Popen(
    [sys.executable, "edge_server.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Give server time to start
time.sleep(2)

# Check if server is still running
if server_process.poll() is not None:
    stdout, stderr = server_process.communicate()
    print("Edge Server failed to start!")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    sys.exit(1)

print("[SUCCESS] Edge Server is running")

# Run vehicle client
print("\n[2/2] Starting Vehicle Client...")
try:
    vehicle_result = subprocess.run(
        [sys.executable, "vehicle.py"],
        capture_output=True,
        text=True,
        timeout=10
    )

    print("\n--- Vehicle Client Output ---")
    print(vehicle_result.stdout)
    if vehicle_result.stderr:
        print("STDERR:", vehicle_result.stderr)

    # Give server time to process
    time.sleep(1)

    # Terminate server and get its output
    server_process.terminate()
    server_stdout, server_stderr = server_process.communicate(timeout=5)

    print("\n--- Edge Server Output ---")
    print(server_stdout)
    if server_stderr:
        print("STDERR:", server_stderr)

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

except subprocess.TimeoutExpired:
    print("Vehicle client timed out!")
    server_process.terminate()
    sys.exit(1)
except Exception as e:
    print(f"Error running test: {e}")
    server_process.terminate()
    sys.exit(1)
