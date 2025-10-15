import os
import pandas as pd
from datetime import datetime

# Path to your CSV (raw string to avoid unicodeescape issues on Windows)
eventlog = eventlog = # add absolute path -> r"C:event_logs.csv"

# Which EventIDs we consider 'critical' (you can edit this list)
CRITICAL_IDS = {1102, 6008, 7045, 4625, 4688, 4624, 4720, 4722, 4725}

# How many sample timestamps to keep per EventID (keeps memory bounded)
SAMPLE_LIMIT = 50


def process_small_file(path: str):
    """
    Read the file into memory (for small-medium files) with memory-savvy dtypes,
    then extract statistics/timestamps for critical EventIDs.
    """
    usecols = ["Timestamp", "EventID", "IP", "Correlation", "ComputerName", "User", "Process"]
    # Parse Timestamp on load and choose efficient dtypes
    dtypes = {
        "EventID": "int32",
        "IP": "category",
        "Correlation": "category",
        "ComputerName": "category",
        "User": "category",
        "Process": "category",
    }

    df = pd.read_csv(path, usecols=usecols, dtype=dtypes, parse_dates=["Timestamp"])
    # Keep a small memory footprint by dropping unused columns later if needed
    df.sort_values("Timestamp", inplace=True)

    results = {}
    for eid in CRITICAL_IDS:
        subset = df[df["EventID"] == eid]
        if subset.empty:
            results[eid] = {
                "count": 0,
                "first": None,
                "last": None,
                "samples": []
            }
            continue

        timestamps = subset["Timestamp"]
        results[eid] = {
            "count": int(len(timestamps)),
            "first": timestamps.iloc[0],
            "last": timestamps.iloc[-1],
            # sample evenly from the series without converting entire column to list
            "samples": list(timestamps.iloc[0:SAMPLE_LIMIT].dt.strftime("%Y-%m-%d %H:%M:%S"))
        }
    return results


def process_large_file_chunked(path: str, chunksize: int = 50_000):
    """
    Stream the CSV in chunks. Maintain compact state per EventID:
      - count
      - earliest timestamp
      - latest timestamp
      - up to SAMPLE_LIMIT sample timestamps (keeps memory O(SAMPLE_LIMIT * num_critical_ids))
    This is O(n) time and O(1) (bounded) extra memory relative to total rows.
    """
    usecols = ["Timestamp", "EventID", "IP", "Correlation"]
    dtypes = {"EventID": "int32", "IP": "category", "Correlation": "category"}

    # Initialize state
    state = {
        eid: {
            "count": 0,
            "first": None,
            "last": None,
            "samples": []
        } for eid in CRITICAL_IDS
    }

    for chunk in pd.read_csv(path, usecols=usecols, dtype=dtypes, parse_dates=["Timestamp"], chunksize=chunksize):
        # iterate only over rows that are critical to avoid scanning everything twice
        critical_chunk = chunk[chunk["EventID"].isin(CRITICAL_IDS)]

        # If empty, quickly continue
        if critical_chunk.empty:
            continue

        # Process by group to reduce Python-level loops
        for eid, group in critical_chunk.groupby("EventID"):
            timestamps = group["Timestamp"].sort_values()
            st = state[eid]

            # Update counts
            st["count"] += int(len(timestamps))

            # Update earliest
            first_ts = timestamps.iloc[0]
            if st["first"] is None or first_ts < st["first"]:
                st["first"] = first_ts

            # Update latest
            last_ts = timestamps.iloc[-1]
            if st["last"] is None or last_ts > st["last"]:
                st["last"] = last_ts

            # Add sample timestamps up to SAMPLE_LIMIT
            if len(st["samples"]) < SAMPLE_LIMIT:
                remaining = SAMPLE_LIMIT - len(st["samples"])
                st["samples"].extend(timestamps.iloc[:remaining].dt.strftime("%Y-%m-%d %H:%M:%S").tolist())

    return state


def pretty_print_results(results: dict):
    for eid in sorted(results.keys()):
        info = results[eid]
        print(f"EventID: {eid}")
        print(f"  Count : {info['count']}")
        print(f"  First : {info['first']}")
        print(f"  Last  : {info['last']}")
        print(f"  Samples ({len(info['samples'])}):")
        for s in info["samples"][:10]:
            print(f"    - {s}")
        if len(info["samples"]) > 10:
            print(f"    ... ({len(info['samples'])} total samples kept)")
        print("-" * 50)


if __name__ == "__main__":
    # Quick size check to decide whether to load whole file or stream it
    try:
        file_size = os.path.getsize(eventlog)
    except OSError:
        raise SystemExit(f"File not found: {eventlog}")

    # Threshold (bytes). Tune this based on your machine. Here 50MB threshold.
    STREAM_THRESHOLD = 50 * 1024 * 1024

    if file_size <= STREAM_THRESHOLD:
        print("Processing with in-memory method...")
        res = process_small_file(eventlog)
    else:
        print("Large file detected — processing in streaming/chunked mode...")
        res = process_large_file_chunked(eventlog, chunksize=100_000)

    pretty_print_results(res)
