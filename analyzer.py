from pathlib import Path
import os
from google import genai

LOG_FILE = Path("logs/application.log")
REPORT_FILE = Path("reports/analysis_report.txt")


def read_logs():
    if not LOG_FILE.exists():
        print("ERROR: Log file not found.")
        return ""

    return LOG_FILE.read_text(encoding="utf-8")


def analyze_basic(log_data):
    lines = log_data.splitlines()

    errors = []
    warnings = []
    critical = []

    for line in lines:
        if "CRITICAL" in line:
            critical.append(line)
        elif "ERROR" in line:
            errors.append(line)
        elif "WARNING" in line:
            warnings.append(line)

    print("\n===== DEVOPS LOG SUMMARY =====")
    print(f"Total log entries : {len(lines)}")
    print(f"Warnings          : {len(warnings)}")
    print(f"Errors            : {len(errors)}")
    print(f"Critical issues   : {len(critical)}")

    return lines, warnings, errors, critical


def analyze_with_ai(log_data):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("ERROR: GEMINI_API_KEY not found.")
        return ""

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an expert DevOps incident analysis assistant.

Analyze the following application logs:

{log_data}

Provide a clear DevOps incident report with these sections:

1. Overall Status
2. Main Incident
3. Severity
4. Likely Root Cause
5. Evidence From Logs
6. Recommended Actions
7. Priority

Keep the explanation practical and easy for a DevOps engineer to understand.
Do not invent evidence that is not present in the logs.
"""

    chat = client.chats.create(model="gemini-3-flash-preview")
    response = chat.send_message(prompt)

    return response.text


def save_report(log_data, ai_analysis):
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    report = f"""AI-BASED DEVOPS LOG ANALYSIS REPORT
=====================================

Log File:
{LOG_FILE}

AI Analysis
-----------

{ai_analysis}

=====================================
End of Report
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"\nReport saved to: {REPORT_FILE}")


if __name__ == "__main__":
    logs = read_logs()

    if logs:
        lines, warnings, errors, critical = analyze_basic(logs)

        print("\n===== AI DEVOPS ANALYSIS =====")

        ai_result = analyze_with_ai(logs)

        if ai_result:
            print(ai_result)
            save_report(logs, ai_result)