import os
import pandas as pd
from datetime import datetime

# Path to your CSV (raw string)
eventlog = # add absolute path -> r"C:event_logs.csv"

# Define which EventIDs you consider "critical"
CRITICAL_IDS = {1102, 6008, 7045, 4625, 4688, 4624, 4720, 4722, 4725}

# How many sample records to keep per EventID (bounded memory)
SAMPLE_LIMIT = 50


def process_small_file(path: str):
    """
    Loads entire file (for small datasets) and summarizes critical events with descriptions.
    """
    usecols = ["Timestamp", "EventID", "IP", "Description", "User", "ComputerName"]
    dtypes = {
        "EventID": "int32",
        "IP": "category",
        "User": "category",
        "ComputerName": "category",
    }

    df = pd.read_csv(path, usecols=usecols, dtype=dtypes, parse_dates=["Timestamp"])
    df.sort_values("Timestamp", inplace=True)

    results = {}
    for eid in CRITICAL_IDS:
        subset = df[df["EventID"] == eid]
        if subset.empty:
            results[eid] = {"count": 0, "first": None, "last": None, "samples": []}
            continue

        timestamps = subset["Timestamp"]
        descriptions = subset["Description"]

        results[eid] = {
            "count": int(len(timestamps)),
            "first": timestamps.iloc[0],
            "last": timestamps.iloc[-1],
            "samples": [
                (
                    str(timestamps.iloc[i]),
                    descriptions.iloc[i][:200]  # truncate long text
                )
                for i in range(min(SAMPLE_LIMIT, len(timestamps)))
            ],
        }

    return results


def process_large_file_chunked(path: str, chunksize: int = 50_000):
    """
    Stream the file and keep compact stats + description samples for critical EventIDs.
    """
    usecols = ["Timestamp", "EventID", "Description"]
    dtypes = {"EventID": "int32"}

    state = {
        eid: {"count": 0, "first": None, "last": None, "samples": []}
        for eid in CRITICAL_IDS
    }

    for chunk in pd.read_csv(
        path, usecols=usecols, dtype=dtypes, parse_dates=["Timestamp"], chunksize=chunksize
    ):
        critical_chunk = chunk[chunk["EventID"].isin(CRITICAL_IDS)]
        if critical_chunk.empty:
            continue

        for eid, group in critical_chunk.groupby("EventID"):
            timestamps = group["Timestamp"].sort_values()
            st = state[eid]

            st["count"] += int(len(timestamps))
            first_ts = timestamps.iloc[0]
            last_ts = timestamps.iloc[-1]

            if st["first"] is None or first_ts < st["first"]:
                st["first"] = first_ts
            if st["last"] is None or last_ts > st["last"]:
                st["last"] = last_ts

            # Add sample (timestamp, description)
            if len(st["samples"]) < SAMPLE_LIMIT:
                remaining = SAMPLE_LIMIT - len(st["samples"])
                sub = group.nlargest(remaining, "Timestamp")
                st["samples"].extend(
                    [
                        (str(ts), desc[:200])
                        for ts, desc in zip(sub["Timestamp"], sub["Description"])
                    ]
                )

    return state


def pretty_print_results(results: dict):
    for eid in sorted(results.keys()):
        info = results[eid]
        print(f"EventID: {eid}")
        print(f"  Count : {info['count']}")
        print(f"  First : {info['first']}")
        print(f"  Last  : {info['last']}")
        print(f"  Samples ({len(info['samples'])}):")
        for ts, desc in info["samples"][:5]:
            print(f"    - {ts} | {desc}")
        if len(info["samples"]) > 5:
            print(f"    ... ({len(info['samples'])} total samples kept)")
        print("-" * 70)


if __name__ == "__main__":
    try:
        file_size = os.path.getsize(eventlog)
    except OSError:
        raise SystemExit(f"File not found: {eventlog}")

    STREAM_THRESHOLD = 50 * 1024 * 1024  # 50MB
    if file_size <= STREAM_THRESHOLD:
        print("Processing with in-memory method...")
        res = process_small_file(eventlog)
    else:
        print("Large file detected — streaming mode...")
        res = process_large_file_chunked(eventlog, chunksize=100_000)

    pretty_print_results(res)
