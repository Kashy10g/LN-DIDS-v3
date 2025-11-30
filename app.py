#!/usr/bin/env python3
import os
import sqlite3
import datetime
import uuid
import threading
import subprocess
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_from_directory, abort
)

# ------------------------
# Import config and helpers
# ------------------------
try:
    from config import DB_PATH, REPORTS_DIR, LOGS_DIR, TOOLS, EMAIL
except Exception:
    # fallback defaults
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "ln_dids.db")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports", "saved_reports")
    LOGS_DIR = os.path.join(BASE_DIR, "reports", "logs")
    TOOLS = ["nmap", "nikto", "tcpdump"]
    EMAIL = {}

# optional modules
try:
    from reporter import PDFReport
except Exception:
    PDFReport = None

try:
    from email_sender import send_email_with_attachments
except Exception:
    send_email_with_attachments = None

# ensure directories
os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("LN_DIDS_SECRET", "change_this_secret_for_prod")

# ------------------------
# Database helpers
# ------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS scans (
        id TEXT PRIMARY KEY,
        target TEXT,
        tools TEXT,
        status TEXT,
        created_at TEXT,
        report_path TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        source TEXT,
        level TEXT,
        message TEXT
    )""")
    db.commit()

def add_scan_record(scan_id, target, tools, status="queued", report_path=""):
    db = get_db()
    db.execute("INSERT OR REPLACE INTO scans (id,target,tools,status,created_at,report_path) VALUES (?,?,?,?,?,?)",
               (scan_id, target, ",".join(tools), status, datetime.datetime.utcnow().isoformat(), report_path))
    db.commit()

def update_scan_status(scan_id, status, report_path=None):
    db = get_db()
    if report_path:
        db.execute("UPDATE scans SET status=?, report_path=? WHERE id=?", (status, report_path, scan_id))
    else:
        db.execute("UPDATE scans SET status=? WHERE id=?", (status, scan_id))
    db.commit()

def fetch_scans(limit=50):
    db = get_db()
    cur = db.execute("SELECT * FROM scans ORDER BY created_at DESC LIMIT ?", (limit,))
    return cur.fetchall()

def add_alert(source, level, message):
    db = get_db()
    db.execute("INSERT INTO alerts (time, source, level, message) VALUES (?, ?, ?, ?)",
               (datetime.datetime.utcnow().isoformat(), source, level, message))
    db.commit()

def fetch_alerts(limit=100):
    db = get_db()
    cur = db.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    return cur.fetchall()

init_db()

# ------------------------
# Authentication
# ------------------------
USERS = {"admin": "admin", "kashy": "phase5ready"}
def logged_in():
    return "user" in session

# ------------------------
# Background scan runner
# ------------------------
def run_tools_background(scan_id, target, tools, on_finish=None):
    def worker():
        txtname = f"{scan_id}_report.txt"
        txtpath = os.path.join(REPORTS_DIR, txtname)
        try:
            with open(txtpath, "w", encoding="utf-8") as out:
                out.write(f"LN-DIDS Scan Report\nID: {scan_id}\nTarget: {target}\nTools: {','.join(tools)}\nTime: {datetime.datetime.utcnow().isoformat()}\n\n")
                for t in tools:
                    out.write("="*60 + "\n")
                    out.write(f"TOOL: {t}\n")
                    out.write("-"*60 + "\n")
                    try:
                        proc = subprocess.run([t, target], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
                        out.write(proc.stdout.decode(errors="replace"))
                    except Exception as e:
                        out.write(f"[ERROR] Running {t}: {e}\n")
                        add_alert(scan_id, "error", f"Tool {t} error: {e}")

            pdfpath = None
            if PDFReport:
                try:
                    pdf = PDFReport(f"LN-DIDS Scan Report {scan_id}")
                    pdfpath = pdf.generate_from_txt(txtpath)
                except Exception as e:
                    add_alert(scan_id, "error", f"PDF generation failed: {e}")

            report_path = pdfpath if pdfpath else txtpath
            update_scan_status(scan_id, "done", report_path)
            add_alert(scan_id, "info", f"Scan {scan_id} completed, report: {report_path}")

            if on_finish:
                on_finish(scan_id, report_path)

        except Exception as e:
            update_scan_status(scan_id, "error")
            add_alert(scan_id, "error", f"Scan worker exception: {e}")

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return True

# ------------------------
# Routes
# ------------------------
@app.route("/")
def index():
    return redirect(url_for("dashboard")) if logged_in() else redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method=="POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        if username in USERS and USERS[username]==password:
            session["user"] = username
            flash("Logged in successfully.", "info")
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"
            add_alert("auth","warning",f"Failed login attempt for {username}")
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if not logged_in(): return redirect(url_for("login"))
    alerts = fetch_alerts(50)
    reports = sorted([f for f in os.listdir(REPORTS_DIR) if os.path.isfile(os.path.join(REPORTS_DIR,f))], reverse=True)[:50]
    return render_template("dashboard.html", tools=TOOLS, alerts=alerts, reports=reports, user=session.get("user"))

@app.route("/run_custom_scan", methods=["POST"])
def run_custom_scan():
    if not logged_in(): return redirect(url_for("login"))
    target = (request.form.get("target") or "").strip()
    tools = request.form.getlist("tools")
    email_addr = (request.form.get("email_address") or "").strip()

    if not target or not tools:
        flash("Provide a target and select at least one tool.", "error")
        return redirect(url_for("dashboard"))

    scan_id = str(uuid.uuid4())[:8]
    add_scan_record(scan_id, target, tools, status="queued")
    add_alert(scan_id, "info", f"Queued scan for {target} with {','.join(tools)}")

    def on_finish(sid, reportpath):
        recipient = email_addr if email_addr else EMAIL.get("receiver_email") or EMAIL.get("sender_email")
        if recipient:
            subject = f"LN-DIDS Scan Report {sid}"
            body = f"Scan {sid} finished. Report attached.\n\nTarget: {target}\nTools: {', '.join(tools)}"
            attachments = [reportpath] if os.path.exists(reportpath) else []
            try:
                ok, msg = send_email_with_attachments(recipient, subject, body, attachments)
                if ok:
                    add_alert(sid,"info",f"Email sent to {recipient}")
                else:
                    add_alert(sid,"error",f"Email failed: {msg}")
            except Exception as e:
                add_alert(sid,"error",f"Email send exception: {e}")
        else:
            add_alert(sid,"warning","No recipient configured; email skipped.")

    update_scan_status(scan_id,"running")
    run_tools_background(scan_id, target, tools, on_finish)
    flash(f"Scan started: {scan_id}", "info")
    return redirect(url_for("dashboard"))

@app.route("/scans")
def scans():
    if not logged_in(): return redirect(url_for("login"))
    return render_template("scans.html", scans=fetch_scans(200))

@app.route("/get_report/<path:filename>")
def get_report(filename):
    if not logged_in(): return redirect(url_for("login"))
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)

@app.route("/alerts")
def alerts_api():
    if not logged_in(): return redirect(url_for("login"))
    return jsonify([dict(r) for r in fetch_alerts(200)])

@app.route("/logs")
def logs():
    if not logged_in(): return redirect(url_for("login"))
    files = sorted(os.listdir(LOGS_DIR), reverse=True)
    return render_template("logs.html", logs=files)

@app.route("/settings")
def settings():
    if not logged_in(): return redirect(url_for("login"))
    return render_template("settings.html")

@app.route("/backup")
def backup():
    if not logged_in(): return redirect(url_for("login"))
    return render_template("backup.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"),404

# ------------------------
# Run server
# ------------------------
if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
