LN-DIDS v3 — Live Network Detection, Identification & Defense System
A Real-Time Cybersecurity Threat Detection & Automation Framework
🚀 What Is LN-DIDS?

LN-DIDS means:

Live Network – Detection, Identification & Defense System

It is a real-time cybersecurity automation platform designed to help cybersecurity analysts, penetration testers, and SOC teams detect, identify, and respond to threats faster.

LN-DIDS integrates multiple security capabilities into one system:

✔ Network scanning
✔ Vulnerability intelligence
✔ System auditing
✔ Device fingerprinting
✔ Authentication detection
✔ Event logging
✔ Email alerting
✔ Web dashboard UI

🔥 Why This Project Is Important

Modern cybersecurity workers face:

Too many tools

Too many alerts

Too much manual work

No unified way to automate detection

Difficulty collecting evidence fast

LN-DIDS solves this.

It combines 8–11 essential cybersecurity tools into one platform with a simple dashboard that:

✔ Runs automated security scans
✔ Sends detection alerts to email
✔ Helps investigate issues faster
✔ Can be used on real client environments
✔ Works for pentesting, SOC, blue team, red team

This is the kind of project that gets cybersecurity jobs because it shows:

Automation skills

Security engineering

Python

Linux/Kali experience

System design

Real-world threat modeling

🛡️ How LN-DIDS Helps Cybersecurity & the World
For companies

Reduces incident response time

Gives small businesses a security dashboard they never had

Helps teams automate routine checks

Lowers cybersecurity cost

Improves overall cyber hygiene

For cyber professionals

Works as an all-in-one everyday toolkit

Helps beginners learn real defense workflows

Helps SOC analysts by giving them a simple unified interface

Helps pentesters organize scans

Helps consultants deliver professional reports

For the world

This project shows how cybersecurity can be:

Accessible

Automated

Affordable

Useful for anyone running a network

LN-DIDS is open-source, so anyone can benefit.

🧩 Tech Stack

Python 3

Flask (Web App)

Jinja2 Templates

Linux / Kali

Bash / Automation Scripts

SMTP Email Integration

Security Tools Integration (Nmap, etc.)

📦 Project Features
✔ Full Web Dashboard
✔ Automated Email Alerts
✔ Multi-tool Scanner Integration
✔ Real-Time Log Monitoring
✔ Modular Plugins (future)
✔ Custom Scan Modes

Level 1 – Full Attack Surface Scan

Level 2 – Medium Scan

Level 3 – Custom User Tool Selection



🖥️ Installation:

git clone https://github.com/Kashy10g/LN-DIDS-v3.git
cd LN-DIDS-v3

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python app.py


📧 Email Configuration

Edit config.py:

MAIL_USERNAME = "your_email"
MAIL_PASSWORD = "your_generated_app_password"
MAIL_RECEIVER = "destination_email"

🚀 Running the App:
 "python app.py"


Open browser:

http://127.0.0.1:5000


🔐 Security Considerations

Never expose your Flask debug server publicly

Use real SMTP with an app password

Sanitize user inputs

Deploy behind Nginx if using externally

🗺️ Roadmap

Add authentication

Add role-based access control

Add full threat database

Add machine-learning anomaly detection

Add detailed reporting engine

📄 License

MIT License
