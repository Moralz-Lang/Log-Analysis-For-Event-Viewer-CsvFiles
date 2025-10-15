import os
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# Path to your CSV (raw string)
eventlog = # add absolute path -> r"C:event_logs.csv"

# Critical Event IDs to track
CRITICAL_IDS = {1102, 6008, 7045, 4625, 4688, 4624, 4720, 4722, 4725}

# How many sample records to keep per EventID (bounded memory)
SAMPLE_LIMIT = 50
CHUNKSIZE = 100_000

# Suspicious keywords for process detection
SUSPICIOUS_KEYWORDS = ["mimikatz", "mimi-katz"]
SUSPICIOUS_PATTERN = re.compile("|".join(re.escape(k) for k in SUSPICIOUS_KEYWORDS), flags=re.IGNORECASE)


def stream_and_aggregate(path: str, chunksize: int = CHUNKSIZE):
    usecols = ["Timestamp", "EventID", "Description", "Process", "ComputerName", "User"]
    dtypes = {"EventID": "Int32", "ComputerName": "category", "User": "category"}

    event_hour_counts = defaultdict(lambda: defaultdict(int))
    suspicious_hits = []
    state = {eid: {"count": 0, "first": None, "last": None, "samples": []} for eid in CRITICAL_IDS}

    reader = pd.read_csv(path, usecols=usecols, dtype=dtypes, parse_dates=["Timestamp"], chunksize=chunksize)

    for chunk in reader:
        chunk = chunk.dropna(subset=["Timestamp"])
        chunk["hour"] = chunk["Timestamp"].dt.floor("h")  # use lowercase 'h'

        chunk = chunk[chunk["EventID"].notna()]
        chunk["EventID"] = chunk["EventID"].astype(int)

        # Convert Description and Process to strings
        chunk["Description"] = chunk.get("Description", "").astype(str)
        chunk["Process"] = chunk.get("Process", "").astype(str)

        # Detect suspicious hits using regex
        desc_mask = chunk["Description"].str.contains(SUSPICIOUS_PATTERN, na=False)
        proc_mask = chunk["Process"].str.contains(SUSPICIOUS_PATTERN, na=False)
        suspicious_mask = desc_mask | proc_mask

        if suspicious_mask.any():
            matches = chunk[suspicious_mask]
            for _, r in matches.iterrows():
                suspicious_hits.append(
                    (r["Timestamp"], int(r["EventID"]), (r.get("Description") or "")[:300], (r.get("Process") or ""))
                )

        # Aggregate counts by hour and EventID
        grouped = chunk.groupby(["hour", "EventID"], sort=False).size()
        for (hour, eid), cnt in grouped.items():
            event_hour_counts[hour][int(eid)] += int(cnt)

        # Update compact state per critical EventID
        critical_rows = chunk[chunk["EventID"].isin(CRITICAL_IDS)]
        if not critical_rows.empty:
            for eid, group in critical_rows.groupby("EventID"):
                st = state[int(eid)]
                timestamps = group["Timestamp"].sort_values()
                st["count"] += int(len(timestamps))
                first_ts = timestamps.iloc[0]
                last_ts = timestamps.iloc[-1]
                if st["first"] is None or first_ts < st["first"]:
                    st["first"] = first_ts
                if st["last"] is None or last_ts > st["last"]:
                    st["last"] = last_ts

                if len(st["samples"]) < SAMPLE_LIMIT:
                    remaining = SAMPLE_LIMIT - len(st["samples"])
                    sample_rows = group.sort_values("Timestamp").head(remaining)
                    for _, r in sample_rows.iterrows():
                        st["samples"].append((r["Timestamp"], (r.get("Description") or "")[:300]))

    return event_hour_counts, suspicious_hits, state


def build_hourly_dataframe(event_hour_counts: dict, critical_ids=CRITICAL_IDS):
    if not event_hour_counts:
        return pd.DataFrame(columns=sorted(critical_ids))

    rows = []
    for hour, cntdict in event_hour_counts.items():
        row = {"hour": hour}
        for eid in critical_ids:
            row[eid] = cntdict.get(eid, 0)
        rows.append(row)

    df = pd.DataFrame(rows).set_index("hour").sort_index()
    idx = pd.date_range(start=df.index.min(), end=df.index.max(), freq="H")
    df = df.reindex(idx, fill_value=0)
    df.index.name = "hour"
    return df


def plot_timeline(hourly_df: pd.DataFrame, suspicious_hits: list, title: str = "Critical Event Timeline"):
    if hourly_df.empty:
        print("No hourly data to plot.")
        return

    fig, ax = plt.subplots(figsize=(14, 6))
    cmap = plt.get_cmap("tab10")
    eids = list(hourly_df.columns)
    linestyles = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 2)), (0, (1, 1))]

    # Plot critical EventID lines
    for i, eid in enumerate(eids):
        color = cmap(i % 10)
        ls = linestyles[i % len(linestyles)]
        ax.plot(
            hourly_df.index,
            hourly_df[eid],
            label=str(eid),
            linewidth=2.2,
            linestyle=ls,
            alpha=0.9,
            color=color
        )

    # Suspicious markers
    if suspicious_hits:
        max_per_hour = hourly_df.max(axis=1)
        xs, ys, labels = [], [], []
        for ts, eid, desc, proc in suspicious_hits:
            hour = pd.Timestamp(ts).floor("h")
            if hour in hourly_df.index:
                base = max_per_hour.loc[hour]
                y = (base + 0.5) if base >= 0 else 0.5
                xs.append(pd.Timestamp(ts))
                ys.append(y)
                labels.append(f"{eid} | {proc} | {desc[:120]}")

        if xs:
            ax.scatter(
                xs,
                ys,
                marker="X",
                s=120,
                facecolor="red",
                edgecolors="black",
                linewidths=1.5,
                label="Suspicious (mimikatz)",
                zorder=12
            )

            for i, lab in enumerate(labels[:8]):
                ax.annotate(
                    lab,
                    (xs[i], ys[i]),
                    textcoords="offset points",
                    xytext=(6, 6),
                    fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=0.3),
                    zorder=13
                )

    ax.xaxis.set_tick_params(rotation=25)
    fig.autofmt_xdate()
    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlabel("Time (hour)")
    ax.set_ylabel("Event Count (per hour)")
    ax.legend(title="EventID", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)

    plt.tight_layout()
    # Save BEFORE showing
    outpath = "timeline.png"
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    print(f"Saved timeline image to: {os.path.abspath(outpath)}")
    plt.show()
    plt.close(fig)


def pretty_print_state(state: dict, top_n_samples: int = 3):
    for eid in sorted(state.keys()):
        info = state[eid]
        print(f"EventID: {eid}")
        print(f"  Count: {info['count']}")
        print(f"  First: {info['first']}")
        print(f"  Last : {info['last']}")
        print(f"  Samples (up to {top_n_samples} shown):")
        for ts, desc in info['samples'][:top_n_samples]:
            print(f"    - {ts} | {desc[:140]}")
        print("-" * 72)


if __name__ == "__main__":
    try:
        file_size = os.path.getsize(eventlog)
    except OSError:
        raise SystemExit(f"File not found: {eventlog}")

    event_hour_counts, suspicious_hits, state = stream_and_aggregate(eventlog, chunksize=CHUNKSIZE)
    hourly_df = build_hourly_dataframe(event_hour_counts)

    pretty_print_state(state, top_n_samples=3)
    print(f"Total suspicious hits (mimikatz-like): {len(suspicious_hits)}")
    if len(suspicious_hits) > 0:
        print("Sample suspicious hit:", suspicious_hits[0])

    plot_timeline(hourly_df, suspicious_hits, title="Critical Event Timeline (hourly) with Suspicious Hits")
