#!/usr/bin/env python3
import os

# ------------------------
# Base paths
# ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Working directories
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports", "saved_reports")
LOGS_DIR = os.path.join(BASE_DIR, "reports", "logs")

# Ensure required folders exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ------------------------
# Tools list (must match what your UI expects)
# ------------------------
TOOLS = [
    "nmap",
    "tcpdump",
    "whatweb",
    "wafw00f",
    "nikto",
    "sslscan",
    "dnsrecon",
    "whois",
    "netcat"
]

# ------------------------
# Email configuration
# MUST match app.py + email_sender.py EXACTLY
# ------------------------
EMAIL = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,

    # MAIN sender Gmail account
    "sender_email": "kashman10g@gmail.com",

    # fallback receiver (used automatically IF form email empty)
    "receiver_email": "kashman10g@gmail.com",

    # Gmail App Password ONLY
    "app_password": "dhvy rzum tphy qjhh",

    # TLS must remain True for Gmail
    "use_tls": True
}

# ------------------------
# Database path
# ------------------------
DB_PATH = os.path.join(BASE_DIR, "ln_dids.db")

