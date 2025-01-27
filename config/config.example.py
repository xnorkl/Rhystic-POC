"""
Configuration settings for the Rhystic server.
Copy this file to config.py and modify as needed.
"""

# Debug mode (disable in production)
DEBUG = True

# Server settings
HOST = "0.0.0.0"
PORT = 8080
ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "https://rhystic.io"
]

# WebRTC settings
MAX_PEERS_PER_ROOM = 8
PEER_CONNECTION_TIMEOUT = 30  # seconds

# TURN server configuration
TURN_SERVERS = {
    "development": {
        "server_url": "localhost",
        "realm": "localhost",
        "auth_secret": "development_secret_key",
        "ports": {
            "tcp": 3478,
            "udp": 3478,
            "tls": 5349
        }
    },
    "production": {
        "server_url": "turn1.rhystic.io",
        "realm": "rhystic.io",
        "auth_secret": "your_production_secret_key_here",
        "ports": {
            "tcp": 3478,
            "udp": 3478,
            "tls": 5349
        }
    }
}

# Security settings
AUTH_TOKEN_EXPIRY = 3600  # 1 hour
CREDENTIAL_ROTATION = 3600  # 1 hour
HMAC_KEY = "change_this_to_a_secure_key"

# Rate limiting
RATE_LIMIT = {
    "requests_per_minute": 60,
    "burst_size": 10
}

# Logging configuration
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
LOG_FORMAT = "structured"  # or "text"
LOG_FILE = "server.log"

# Monitoring
ENABLE_METRICS = True
METRICS_PORT = 9090

# Development settings (ignored in production)
DEV_AUTO_RELOAD = True
DEV_STATIC_FILES = True 