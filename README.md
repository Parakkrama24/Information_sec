# Secure V2I Communication System

A complete Vehicle-to-Infrastructure (V2I) communication protocol with end-to-end encryption, authentication, and a modern web dashboard for testing and monitoring.

## Overview

This project implements a secure communication protocol between vehicles and edge infrastructure using industry-standard cryptographic techniques:

- **RSA-2048**: Asymmetric encryption for authentication and key exchange
- **AES-256-GCM**: Symmetric encryption for data confidentiality and integrity
- **Digital Signatures**: RSA-PSS for non-repudiation and integrity verification
- **Challenge-Response**: Cryptographic authentication mechanism

## Project Structure

```
Secure_V2I_Communication/
├── keys_setup.py           # RSA key pair generation
├── edge_server.py          # Infrastructure endpoint (edge server)
├── vehicle.py              # Vehicle client implementation
├── test_system.py          # Automated testing script
├── api_server.py           # Flask REST API for web dashboard
├── start_dashboard.py      # Dashboard launcher (cross-platform)
├── start_dashboard.bat     # Dashboard launcher (Windows)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── walkthrough.md          # Detailed protocol walkthrough
├── *.pem                   # RSA key files (generated)
└── UI/                     # Web Dashboard
    ├── index.html          # Dashboard HTML
    ├── styles.css          # Styling
    ├── script.js           # Frontend logic
    └── README.md           # UI documentation
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `cryptography` - For RSA and AES operations
- `flask` - Web framework for API server
- `flask-cors` - CORS support for API

### 2. Generate Cryptographic Keys

```bash
python keys_setup.py
```

This creates RSA key pairs for both vehicle and edge server:
- `vehicle_private.pem` & `vehicle_public.pem`
- `edge_server_private.pem` & `edge_server_public.pem`

### 3. Choose Your Interface

#### Option A: Web Dashboard (Recommended)

**Windows:**
```bash
start_dashboard.bat
```

**Linux/Mac or Python:**
```bash
python start_dashboard.py
```

The dashboard will automatically:
- Start the API server on `http://localhost:5000`
- Open the web interface in your browser
- Allow you to run tests and view logs in real-time

#### Option B: Command Line Testing

**Automated Test:**
```bash
python test_system.py
```

**Manual Testing (two terminals):**

Terminal 1:
```bash
python edge_server.py
```

Terminal 2:
```bash
python vehicle.py
```

## Features

### Security Protocol

1. **Connection Establishment**: TCP socket connection between vehicle and edge server
2. **Authentication**: Edge server sends cryptographic challenge, vehicle signs with private key
3. **Key Exchange**: Vehicle generates AES session key, encrypts with server's public key
4. **Secure Transmission**: Vehicle data encrypted with AES-GCM and signed for integrity

### Web Dashboard

- **Project Details**: Complete protocol documentation and specifications
- **Folder Structure**: Interactive project file explorer
- **Testing Interface**:
  - One-click full system test
  - Manual server/client control
  - Real-time log streaming
  - Telemetry data visualization
  - Color-coded success/error messages

### Technical Specifications

| Component | Technology |
|-----------|-----------|
| Asymmetric Encryption | RSA-2048 |
| Symmetric Encryption | AES-256-GCM |
| Hash Algorithm | SHA-256 |
| Signature Scheme | RSA-PSS (PKCS#1 v2.1) |
| Transport Protocol | TCP/IP |
| Server Port | 65432 |
| API Port | 5000 |

## Usage Examples

### Running a Full Test

```bash
# Command Line
python test_system.py

# Web Dashboard
# Click "Run Full Test" button
```

### Starting Services Individually

```bash
# Start Edge Server
python edge_server.py

# In another terminal, run vehicle client
python vehicle.py

# Start API server for web dashboard
python api_server.py
```

### Sample Output

**Edge Server:**
```
Starting Edge Server...
Keys loaded successfully.
Edge Server listening on 127.0.0.1:65432
Connected by Vehicle at ('127.0.0.1', 58030)
[SUCCESS] Vehicle Authentication Verified!
[SUCCESS] AES Session Key successfully decrypted!
[SUCCESS] Payload Signature Verified!

--- SECURE VEHICLE STATE RECEIVED ---
{
    "vehicle_id": "V-4848",
    "position": {"x": 42.3601, "y": -71.0589},
    "velocity": 65.5,
    "qos_level": 2,
    "privacy_demand_psi": 0.85
}
```

## API Endpoints

The Flask API server provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/folder-structure` - Get project directory tree
- `POST /api/start-server` - Start edge server
- `POST /api/stop-server` - Stop edge server
- `POST /api/run-vehicle` - Run vehicle client
- `POST /api/run-full-test` - Run complete system test
- `GET /api/server-logs` - Get edge server logs
- `GET /api/telemetry` - Get received telemetry data

## Security Features

### Confidentiality
- Vehicle telemetry encrypted with AES-256-GCM
- Session key protected by RSA-2048 encryption

### Integrity
- Digital signatures on all critical data
- AES-GCM provides authenticated encryption

### Authentication
- Challenge-response protocol verifies vehicle identity
- RSA signatures prove possession of private key

### Non-repudiation
- All transmissions digitally signed
- Cryptographic proof of message origin

## Development

### Adding New Features

1. **Modify Protocol**: Edit `edge_server.py` and `vehicle.py`
2. **Update Tests**: Modify `test_system.py`
3. **Add API Endpoints**: Edit `api_server.py`
4. **Update UI**: Modify files in `UI/` directory

### Running in Debug Mode

```python
# In api_server.py, change:
app.run(host='0.0.0.0', port=5000, debug=True)
```

## Troubleshooting

**Keys not found error:**
```bash
python keys_setup.py
```

**Port already in use:**
- Change port in `edge_server.py` (PORT variable)
- Or stop the conflicting process

**API server connection failed:**
- Ensure Flask is installed: `pip install flask flask-cors`
- Check firewall settings
- Verify port 5000 is available

**Browser shows "Backend not available":**
- Make sure `api_server.py` is running
- Check console for errors
- Try accessing `http://localhost:5000/api/health`

## Use Cases

- **Academic Projects**: Information security coursework demonstration
- **IoT Security**: Template for secure device-to-server communication
- **V2X Research**: Foundation for vehicle-to-everything communication protocols
- **Security Training**: Learning cryptographic protocol implementation

## Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Windows/Linux/macOS

## License

This is an educational project for information security coursework.

## Contributing

This project is designed for educational purposes. Feel free to:
- Report issues
- Suggest improvements
- Fork for your own projects
- Use as a reference for security implementations

## Acknowledgments

Built using:
- Python `cryptography` library
- Flask web framework
- Modern web technologies (HTML5, CSS3, JavaScript)

## Author

Created as part of Information Security coursework (EC7201)

## Future Enhancements

- [ ] Add support for multiple concurrent vehicles
- [ ] Implement certificate-based authentication (PKI)
- [ ] Add mutual TLS for transport security
- [ ] Database storage for telemetry history
- [ ] Real-time dashboard updates via WebSockets
- [ ] Vehicle simulation with random telemetry
- [ ] Geographic mapping of vehicle positions
- [ ] Performance metrics and analytics
#   I n f o r m a t i o n _ s e c  
 