# tools_runner.py
import subprocess
import threading
import os
from config import REPORTS_DIR

def run_tools_background(scan_id, target, tools, on_finish=None):
    """
    Runs the specified tools on the target in a background thread.
    Saves TXT report to REPORTS_DIR.
    Calls on_finish(scan_id, txt_path) when done.
    """
    def worker():
        os.makedirs(REPORTS_DIR, exist_ok=True)
        report_path = os.path.join(REPORTS_DIR, f"{scan_id}_report.txt")
        output_lines = []

        for tool in tools:
            try:
                cmd = [tool, target]  # Basic command; can extend for tool-specific args
                output_lines.append(f"\n=== Running {tool} on {target} ===\n")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                output_lines.append(result.stdout)
                if result.stderr:
                    output_lines.append(f"ERROR: {result.stderr}\n")
            except FileNotFoundError:
                output_lines.append(f"Tool not found: {tool}\n")
            except subprocess.TimeoutExpired:
                output_lines.append(f"{tool} timed out.\n")
            except Exception as e:
                output_lines.append(f"{tool} failed: {e}\n")

        # Save TXT report
        with open(report_path, "w") as f:
            f.writelines(output_lines)

        # Callback for PDF/email
        if on_finish:
            on_finish(scan_id, report_path)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

