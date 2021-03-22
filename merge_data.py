"""
Merges our human-entered data with the crawled data.
This not generalized at all.
"""
import os
import pandas as pd
import sys

dir_path = sys.argv[1]
original_crawler_records_file = os.path.join(dir_path, 'ttf_crawler_records.csv')
data_files = [f for f in os.listdir(dir_path)
                if not f.endswith('ttf_crawler_records.csv')
                and not os.path.basename(f).startswith('merged_')
                and not os.path.basename(f).startswith('.')]

print dir_path
print original_crawler_records_file
print data_files

data_main = pd.read_csv(original_crawler_records_file)  
data_merged_main = None

for data_fn in data_files:
    data_fp = os.path.join(dir_path, data_fn)
    data = None
    data_merged = None
    data = pd.read_csv(data_fp)
    data_merged = pd.merge(data_main, data, how='right', left_on='uid', right_on='uid_from_crawler', suffixes=(False, False))
    if type(data_merged_main) is pd.core.frame.DataFrame:
        data_merged_main = data_merged_main.append(data_merged)
    else:
        data_merged_main = data_merged
    # data_merged.to_csv(os.path.join(dir_path, 'merged_' + os.path.basename(data_fp)))

data_merged_main.to_csv(os.path.join(dir_path, 'merged_combined_ttf_data.csv'))


