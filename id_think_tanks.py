import pandas as pd

data_main = pd.read_csv('data/ttf_crawler_records_2011-2018.csv')  
think_tanks = set(pd.read_csv('data/think_tanks.csv')['think_tank'])

data_main['think_tank'] = ''

for i, desc in data_main['witness_desc'].iteritems():
	print i
	for tt in think_tanks:
		if tt in str(desc): 
			data_main.at[i, 'think_tank'] = tt
			continue

data_main.to_csv('data/ttf_w_tt_2011-2018.csv')
