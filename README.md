Event Log Analyzer for Security Analysts
Overview

This project provides a scalable, efficient, and visual event log analysis toolkit for Windows environments.
It is designed to help security analysts quickly identify critical events, suspicious processes, and time-correlated activity from large CSV exports of Windows Event Logs.

The toolkit processes large log files in streaming chunks, tracks critical EventIDs, detects suspicious processes (like Mimikatz), and provides hourly aggregation with visual timelines for rapid analysis.

Key Features
1. Critical Event Tracking

Tracks high-priority EventIDs commonly used in security monitoring and incident response, including:

4625 – Failed logon

4624 – Successful logon

4688 – New process creation

4720, 4722, 4725 – User account changes

7045 – Service installation

6008 – Unexpected shutdown

1102 – Event log cleared

Maintains compact state per EventID, including:

Count of occurrences

First and last timestamps

Sample descriptions (bounded for memory efficiency)

2. Suspicious Process Detection

Detects keywords such as mimikatz in both Description and Process columns.

Supports vectorized, regex-based detection for fast identification of potential malware or credential dumping.

Stores suspicious hits with timestamp, EventID, and truncated context for quick forensic review.

3. Hourly Aggregation & Time Correlation

Aggregates events per hour, allowing analysts to spot activity spikes or abnormal patterns.

Supports time correlation between critical events and suspicious processes.

Processes logs in chunks for a compact memory footprint, even on large CSVs (>1M rows).

4. Visualization

Generates timeline plots for critical EventIDs over time.

Highlights suspicious hits with distinct red X markers and optional annotations.

Uses different line styles and colors per EventID for clarity.

Saves high-resolution PNGs for reporting or documentation.

5. Scalable & Robust

Streaming approach handles very large CSV exports without memory overload.

Gracefully handles missing timestamps or descriptions.

Modular functions allow custom filtering, additional EventIDs, or new suspicious keywords.

Installation

Clone the repository:

git clone https://github.com/yourusername/Log-Analysis-For-Event-Viewer-CsvFiles.git
cd Log-Analysis-For-Event-Viewer-CsvFiles


Install dependencies:

pip install pandas matplotlib


Python 3.9+ recommended for best compatibility.

Usage
Run the main analysis
python script4matplotlib.py


The script will:

Stream the CSV file.

Aggregate critical EventIDs per hour.

Detect suspicious processes.

Print a summary of counts, first/last timestamps, and sample descriptions.

Generate a timeline plot highlighting suspicious events.

Customize for Your Environment

Change the CSV path:

eventlog = r"C:\Path\To\Your\EventLogs.csv"


Add custom EventIDs:

CRITICAL_IDS.update({1234, 5678})


Add suspicious keywords:

SUSPICIOUS_KEYWORDS.append("powershell")

Benefits for Security Analysts

Fast triage: Quickly identify critical events and suspicious activity without manually scrolling through logs.

Time correlation: Visualize sequences of events to detect attack patterns, lateral movement, or credential dumping.

Memory-efficient: Handles large CSV exports without requiring high-memory machines.

Forensic-ready samples: Keeps sample descriptions for deeper investigation without storing all events in memory.

Clear visuals: Timeline charts help analysts detect unusual spikes and suspicious behavior immediately.

Example Workflow

Export Windows Event Logs to CSV.

Run the analyzer script.

Review textual summary of critical EventIDs and suspicious hits.

Examine the timeline plot for time-correlated events.

Use sample descriptions to investigate potential threats.

This workflow reduces manual log sifting, saves hours in incident response, and provides actionable insights for security teams.

Contributing

Contributions are welcome! You can:

Add support for additional EventIDs.

Add more suspicious keyword detection.

Integrate with SIEM exports.

Improve visualizations (dark theme, interactivity).

License

MIT License – free to use and modify.
