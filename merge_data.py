"""
Merges our human-entered data with the crawled data.
This not generalized at all.
"""
import pandas as pd

data_main = pd.read_csv('data/2017/ttf_crawler_records.csv')  

data_c = pd.read_csv('data/2017/christine_data_entry.csv')
data_c_merged = pd.merge(data_main, data_c, how='right', left_on='uid', right_on='uid_from_2017_ttfs')
data_c_merged.to_csv('data/2017/merged_ttf_christine.csv')

data_c2 = pd.read_csv('data/2017/christine_data_entry_batch_2.csv')
data_c2_merged = pd.merge(data_main, data_c2, how='right', left_on='uid', right_on='uid_from_2017_ttfs')
data_c2_merged.to_csv('data/2017/merged_ttf_christine_batch_2.csv')

data_c3 = pd.read_csv('data/2017/christine_data_entry_batch_3.csv')
data_c3_merged = pd.merge(data_main, data_c3, how='right', left_on='uid', right_on='uid_from_2017_ttfs')
data_c3_merged.to_csv('data/2017/merged_ttf_christine_batch_3.csv')

data_d = pd.read_csv('data/2017/diego_data_entry.csv')
data_d_merged = pd.merge(data_main, data_d, how='right', left_on='uid', right_on='uid_from_2017_ttfs')
data_d_merged.to_csv('data/2017/merged_ttf_diego.csv')

data_f = pd.read_csv('data/2017/flaviana_data_entry.csv')
data_f_merged = pd.merge(data_main, data_f, how='right', left_on='uid', right_on='uid_from_2017_ttfs')
data_f_merged.to_csv('data/2017/merged_ttf_flaviana.csv')

data_j = pd.read_csv('data/2017/jahnavi_data_entry.csv')
data_j_merged = pd.merge(data_main, data_j, how='right', left_on='uid', right_on='uid_from_2017_ttfs')
data_j_merged.to_csv('data/2017/merged_ttf_jahnavi.csv')

data_merged = data_c_merged.append(data_c2_merged).append(data_c3_merged).append(data_d_merged).append(data_f_merged).append(data_j_merged)
data_merged.to_csv('data/2017/combined_merged_ttf_data.csv')