"""
Concatenates two CSV files of the same structure into one file.
Used to merge the data from each year into one file.

Usage: python merge_csv.py [filepath1 filepath2 ...]
"""
import datetime as dt
import pandas as pd
import sys

files = sys.argv[1:]
print files

frames = [pd.read_csv(f) for f in files]
result = pd.concat(frames)
result.to_csv("merged_" + str(dt.datetime.now()) + ".csv")

