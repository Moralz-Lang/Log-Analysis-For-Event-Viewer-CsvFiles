import os
import pandas as pd
import matplotlib.pyplot as plt

eventlog = # add absolute path -> r"C:event_logs.csv"

analysis = pd.read_csv(eventlog, index_col=["Timestamp", "EventID", "IP", "Correlation"]).sort_index()
print(analysis.head())
#print(analysis.describe())
#print(analysis.nunique())

#print(analysis["EventID"].value_counts())