
Event Log Analyzer for Security Analysts
Overview
This project provides a scalable, efficient, and visual event log analysis toolkit for Windows environments. It is designed to help security analysts quickly identify critical events, suspicious processes, and time-correlated activity from large CSV exports of Windows Event Logs.
The toolkit processes large log files in streaming chunks, tracks critical EventIDs, detects suspicious processes (like Mimikatz), and provides hourly aggregation and visual timelines for fast analysis.

Key Features
1. Critical Event Tracking
    • Tracks high-priority EventIDs commonly used in security monitoring and incident response, such as:
        ◦ 4625 – Failed logon
        ◦ 4624 – Successful logon
        ◦ 4688 – New process creation
        ◦ 4720, 4722, 4725 – User account changes
        ◦ 7045 – Service installation
        ◦ 6008 – Unexpected shutdown
        ◦ 1102 – Event log cleared
    • Maintains compact state per EventID, including:
        ◦ Count of occurrences
        ◦ First and last timestamp
        ◦ Sample descriptions (bounded for memory efficiency)
2. Suspicious Process Detection
    • Detects keywords such as mimikatz in both Description and Process columns.
    • Supports vectorized, regex-based detection to quickly flag potential malware or credential dumping activity.
    • Stores suspicious hits with timestamp, EventID, and truncated context for fast forensic review.
3. Hourly Aggregation and Time Correlation
    • Aggregates events per hour, enabling analysts to quickly spot activity spikes or abnormal patterns.
    • Supports time correlation between critical events and suspicious processes.
    • Provides compact memory footprint, even on large CSVs (>1M rows), by processing logs in chunks.
4. Visualization
    • Generates timeline plots for critical EventIDs over time.
    • Highlights suspicious hits with distinct red X markers and annotations.
    • Uses different line styles and colors per EventID for clear visual separation.
    • Saves high-resolution PNGs for reporting or documentation.
    • Example output:
5. Scalable & Robust
    • Streaming approach allows handling very large CSV exports without memory overload.
    • Handles missing timestamps or descriptions gracefully.
    • Modular functions allow custom filtering, additional EventIDs, or new suspicious keywords.

Installation
    1. Clone the repository:
git clone https://github.com/yourusername/Log-Analysis-For-Event-Viewer-CsvFiles.git
cd Log-Analysis-For-Event-Viewer-CsvFiles
    2. Install dependencies:
pip install pandas matplotlib
Python 3.9+ recommended for best compatibility.

Usage
Run the main analysis
python script4matplotlib.py
The script will:
    1. Stream the CSV file.
    2. Aggregate critical EventIDs per hour.
    3. Detect suspicious processes.
    4. Print a summary of counts, first/last timestamps, and sample descriptions.
    5. Generate a timeline plot highlighting suspicious events.
Customize for your environment
    • Change the CSV path:
eventlog = r"C:\Path\To\Your\EventLogs.csv"
    • Add custom EventIDs:
CRITICAL_IDS.update({1234, 5678})
    • Add suspicious keywords:
SUSPICIOUS_KEYWORDS.append("powershell")

Benefits for Security Analysts
    • Fast triage: Quickly identify critical events and suspicious activity without scrolling through millions of rows.
    • Time correlation: Visualize sequences of events, helping detect attack patterns, lateral movement, or credential dumping.
    • Memory-efficient: Works on large CSV exports without requiring high-memory machines.
    • Forensic-ready samples: Keeps sample descriptions for deeper investigation without storing all events in memory.
    • Clear visuals: Timeline charts help analysts detect unusual spikes and suspicious behavior immediately.

Example Workflow
    1. Export Windows Event Logs to CSV.
    2. Run the analyzer script.
    3. Review textual summary of critical EventIDs and suspicious hits.
    4. Examine the timeline plot for time-correlated events.
    5. Use sample descriptions to investigate potential threats.
This workflow reduces manual log sifting, saves hours in incident response, and provides actionable insight for security teams.

Contributing
Contributions are welcome! You can:
    • Add support for additional EventIDs.
    • Add more suspicious keyword detection.
    • Integrate with SIEM exports.
    • Improve visualizations (dark theme, interactivity).

License
MIT License – free to use and modify.

This README emphasizes practical value for security analysts while explaining the tool’s workflow and scalability.
