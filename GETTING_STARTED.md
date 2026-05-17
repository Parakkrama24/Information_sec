# Getting Started with Secure V2I Communication Dashboard

## Quick Start Guide

The frontend application is now ready! Follow these simple steps:

### Step 1: Start the Backend API Server

The API server is **already running** on `http://localhost:5000`

If you need to restart it later:
```bash
python api_server.py
```

### Step 2: Open the Dashboard

**Method 1 - Double Click (Easiest):**
- Navigate to the `UI` folder
- Double-click `index.html`

**Method 2 - Command Line:**
```bash
start UI\index.html
```

**Method 3 - Use the Launcher:**
```bash
python start_dashboard.py
```
or
```bash
start_dashboard.bat
```

### Step 3: Use the Dashboard

Once the dashboard opens in your browser:

1. **Navigate** using the top menu bar:
   - **Project Details** - Learn about the security protocol
   - **Folder Structure** - See the project file organization
   - **Testing & Logs** - Test the system and view real-time logs

2. **Run Tests**:
   - Click **"Run Full Test"** to test the entire system
   - Or use **"Start Edge Server"** → **"Run Vehicle Client"** for manual testing

3. **View Results**:
   - Watch real-time logs appear in the log windows
   - See the received telemetry data
   - Color-coded messages (green = success, red = error, blue = info)

## Dashboard Features

### Page 1: Project Details
- Overview of the V2I communication protocol
- Security features (Authentication, Key Exchange, Confidentiality, Integrity)
- Protocol phases with detailed explanations
- Technical specifications table
- Sample telemetry data

### Page 2: Folder Structure
- Interactive project directory tree
- Detailed file descriptions
- Icons for different file types

### Page 3: Testing & Logs
- **System Status** indicators for Edge Server and Vehicle
- **Test Controls**:
  - Start/Stop Edge Server
  - Run Vehicle Client
  - Run Full System Test
  - Clear Logs
- **Real-time Logs**:
  - Edge Server logs
  - Vehicle Client logs
  - Received telemetry data display

## API Endpoints (for developers)

If you want to integrate with the API directly:

```bash
# Health check
curl http://localhost:5000/api/health

# Get folder structure
curl http://localhost:5000/api/folder-structure

# Run full test
curl -X POST http://localhost:5000/api/run-full-test

# Start edge server
curl -X POST http://localhost:5000/api/start-server

# Run vehicle client
curl -X POST http://localhost:5000/api/run-vehicle

# Stop edge server
curl -X POST http://localhost:5000/api/stop-server

# Get server logs
curl http://localhost:5000/api/server-logs

# Get telemetry data
curl http://localhost:5000/api/telemetry
```

## Troubleshooting

**Dashboard shows "Backend server not available":**
- Make sure the API server is running: `python api_server.py`
- Check that nothing else is using port 5000

**Test buttons don't work:**
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure RSA keys exist (run `python keys_setup.py` if needed)

**Browser doesn't open automatically:**
- Manually navigate to `UI\index.html`
- Or open `http://localhost:5000` if using a future web-server version

## What's Been Created

```
UI/
├── index.html       ✅ Main dashboard with 3 pages
├── styles.css       ✅ Modern dark theme styling
├── script.js        ✅ Interactive functionality & API integration
└── README.md        ✅ UI documentation

api_server.py        ✅ Flask REST API backend
start_dashboard.py   ✅ Cross-platform launcher
start_dashboard.bat  ✅ Windows launcher
README.md            ✅ Complete project documentation
GETTING_STARTED.md   ✅ This quick start guide
```

## Current Status

✅ API Server: **RUNNING** on http://localhost:5000
✅ Dashboard: **READY** at UI/index.html
✅ Backend Tests: **PASSING**
✅ All Features: **WORKING**

## Next Steps

1. Open `UI\index.html` in your browser
2. Click "Run Full Test" to see it in action
3. Explore the three pages using the navigation bar
4. View logs and telemetry data in real-time

Enjoy your Secure V2I Communication Dashboard!
