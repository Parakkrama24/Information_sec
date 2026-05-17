# Secure V2I Communication - Web Dashboard

A modern web-based dashboard for managing and testing the Secure V2I Communication system.

## Features

- **Project Details**: Overview of the V2I communication protocol, security features, and technical specifications
- **Folder Structure**: Interactive view of the project directory structure with file descriptions
- **Testing & Logs**: Real-time testing interface with live log viewing for both edge server and vehicle client

## Quick Start

### 1. Install Dependencies

Make sure you have Python installed, then run:

```bash
pip install -r ../requirements.txt
```

### 2. Start the API Server

From the project root directory, run:

```bash
python api_server.py
```

The API server will start on `http://localhost:5000`

### 3. Open the Dashboard

Simply open `index.html` in your web browser:

```bash
# On Windows
start index.html

# On macOS
open index.html

# On Linux
xdg-open index.html
```

Or navigate to the UI folder and double-click `index.html`

## Usage

### Testing the System

1. **Full System Test** (Recommended for first-time users):
   - Click "Run Full Test" button
   - This will automatically start the edge server and run the vehicle client
   - View logs and telemetry data in real-time

2. **Manual Testing**:
   - Click "Start Edge Server" to start the server
   - Wait for server to be active
   - Click "Run Vehicle Client" to send test data
   - View logs from both components

3. **Stop Server**:
   - Click "Stop Server" to terminate the edge server

### Navigation

- **Project Details**: Learn about the security protocol and technical implementation
- **Folder Structure**: Explore the project files and their purposes
- **Testing & Logs**: Run tests and view real-time system logs

## Architecture

```
UI/
├── index.html       # Main dashboard page
├── styles.css       # Modern dark theme styling
├── script.js        # Frontend JavaScript logic
└── README.md        # This file

../api_server.py     # Flask backend API
```

## API Endpoints

The backend provides the following REST API endpoints:

- `GET /api/health` - Health check
- `GET /api/folder-structure` - Get project directory tree
- `POST /api/start-server` - Start edge server
- `POST /api/stop-server` - Stop edge server
- `POST /api/run-vehicle` - Run vehicle client
- `POST /api/run-full-test` - Run complete system test
- `GET /api/server-logs` - Get edge server logs
- `GET /api/telemetry` - Get received telemetry data

## Technologies Used

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Flask (Python), Flask-CORS
- **Security**: Cryptography library for RSA and AES operations

## Features

- Modern dark-themed UI with gradient accents
- Real-time log streaming
- Color-coded log messages (success/error/info)
- Responsive design for mobile and desktop
- Status indicators for system components
- JSON telemetry data viewer

## Troubleshooting

**Dashboard shows "Backend server not available"**
- Make sure `api_server.py` is running
- Check that it's running on port 5000
- Verify no firewall is blocking the connection

**Test buttons don't work**
- Ensure all dependencies are installed (`pip install -r requirements.txt`)
- Check that RSA keys are generated (run `python keys_setup.py`)
- Verify the console for any JavaScript errors

**No logs appearing**
- Check browser console for errors
- Verify API server is running and accessible
- Try clearing logs and running test again

## Security Note

This dashboard is for development and demonstration purposes. In production:
- Add authentication to API endpoints
- Use HTTPS for secure communication
- Implement rate limiting
- Add input validation and sanitization
