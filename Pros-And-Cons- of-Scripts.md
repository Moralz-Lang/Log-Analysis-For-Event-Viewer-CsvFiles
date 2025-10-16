# Event Log Analysis Scripts — Comparative Review

## Script 1 — Initial CSV Read + Basic Analysis

```python
import os
import pandas as pd
import matplotlib.pyplot as plt

eventlog = r"C:\...\event_logs.csv"
analysis = pd.read_csv(eventlog, index_col=["Timestamp", "EventID", "IP", "Correlation"]).sort_index()
print(analysis.head())
```

**Pros:**

* Simple and easy to understand.
* Quick to load small CSVs and inspect data snapshot.
* Uses `sort_index()` to prepare data for indexing.

**Cons:**

* Not scalable: loads entire CSV into memory.
* No aggregation or event analysis; purely basic display.
* Does not handle missing or malformed data.
* No suspicious/malware detection or visualization beyond `head()`.
* Hard-coded `index_col` may break with different CSV schemas.

**Verdict:**
Good starting point for small datasets; purely exploratory.

---

## Script 2 — EventID Analysis + Description Handling

```python
analysis = pd.read_csv(eventlog, index_col=["Timestamp", "EventID", "IP", "Correlation"]).sort_index()
print(analysis.head())
analysis["date"] = pd.to_datetime(analysis['date'])
```

**Pros:**

* Adds handling for description fields and timestamps.
* Prepares data for event-focused analysis (critical events, counts).
* Slightly more robust than Script 1.

**Cons:**

* Still in-memory; large CSVs may cause memory issues.
* Cannot detect suspicious activity like Mimikatz.
* Limited processing: only supports `head()` and `describe()`.
* Time conversions exist but are not leveraged.

**Verdict:**
Slightly more useful than Script 1, but still not scalable or analyst-ready.

---

## Script 3 — Streaming + Critical EventID + Suspicious Process Detection

* Introduced `stream_and_aggregate()` function.
* Chunked reading for large CSVs.
* Tracks **CRITICAL_IDS**; maintains compact state (count, first/last timestamps, sample descriptions).
* Detects suspicious keywords in `Description` and `Process`.

**Pros:**

* Memory-efficient: streams chunks instead of loading full CSV.
* Tracks per-hour counts for analysis.
* Bounded memory samples for each critical EventID.
* Supports regex-based suspicious activity detection.
* Scales well for production logs (100k+ rows).

**Cons:**

* Initial plotting not integrated.
* Lines and markers in plots were visually indistinct; markers overlapped lines.
* FutureWarnings (`.dt.floor("H")`) and categorical issues in pandas.
* Visualization lacked clarity for analysts.

**Verdict:**
Major improvement for forensic-ready analysis; efficient and scalable, but visualization needed refinement.

---

## Script 4 — Full-Featured Timeline Visualization + Improved Plotting

* Built on Script 3:

  * Distinct line styles and linewidth per EventID.
  * Bold X markers for suspicious hits.
  * Top-N annotations for suspicious events.
  * Corrected `plt.savefig()` usage to avoid blank files.
  * Tight layout, rotated x-axis for readability.
* Handles large datasets efficiently via streaming.
* Fully integrates **critical event analysis, suspicious process detection, and time correlation visualization**.

**Pros:**

* Clear visuals + textual summary for analysts.
* Memory- and time-efficient: chunked processing, bounded samples.
* Suspicious events highlighted clearly.
* Modular and extendable (`stream_and_aggregate`, `build_hourly_dataframe`, `plot_timeline`).
* Robust to missing timestamps or descriptions.
* Scalable to very large CSVs (100k–1M+ rows).

**Cons:**

* Slightly more complex for beginners.
* Linear aggregation; could be optimized further with vectorized operations for extreme datasets.
* Annotations can become cluttered with many suspicious events in one hour.
* Matplotlib interactive issues on headless servers (may need Agg backend).

**Verdict:**
Most complete and professional. Combines analysis, streaming efficiency, and visualization; ready for real forensic workflows.

---

## Comparison Summary Table

| Feature / Script                   | 1 | 2 | 3 | 4 |
| ---------------------------------- | - | - | - | - |
| Reads CSV                          | ✅ | ✅ | ✅ | ✅ |
| Handles large datasets             | ❌ | ❌ | ✅ | ✅ |
| Tracks critical EventID            | ❌ | ❌ | ✅ | ✅ |
| Suspicious process detection       | ❌ | ❌ | ✅ | ✅ |
| Aggregates by hour                 | ❌ | ❌ | ✅ | ✅ |
| Keeps sample logs for forensic use | ❌ | ❌ | ✅ | ✅ |
| Matplotlib visualization           | ❌ | ❌ | ❌ | ✅ |
| Distinct lines / markers           | ❌ | ❌ | ❌ | ✅ |
| Save figure reliably               | ❌ | ❌ | ❌ | ✅ |
| Modular / maintainable             | ❌ | ❌ | ✅ | ✅ |
| Robust to missing/malformed data   | ❌ | ❌ | ✅ | ✅ |

---

## Key Takeaways

1. **Script 1 → Script 2:** Exploration → minor preprocessing. Suitable only for small datasets.
2. **Script 3:** Big step for scalability and analyst readiness; memory-efficient and focuses on critical events.
3. **Script 4:** Fully polished, ready for professional forensic/SOC use; clear visual cues, reliable saving, scalable processing.

