import sys
import pandas as pd

data_main = pd.read_csv(sys.argv[1])  

think_tanks = [
	"American Enterprise Institute",
	"Aspen Institute",
	"Atlantic Council",
	"Brookings Institution",
	"Carnegie Council for Ethics in International Affairs",
	"Carnegie Endowment for International Peace",
	"Center for American Progress",
	"Center for Global Development",
	"Center for New American Security",
	"Center for Strategic and International Studies",
	"Center on Budget and Policy Priorities",
	"Council on Foreign Relations",
	"EastWest Institute",
	"Freedom House",
	"German Marshall Fund of the United States",
	"Hoover Institution",
	"Inter-American Dialogue",
	"International Food Policy Research Institute",
	"James A. Baker III Institute for Public Policy",
	"Middle East Institute",
	"Peterson Institute for International Economics",
	"RAND Corporation",
	"Recources For the Future",
	"Stimson Center",
	"Urban Institute",
	"Woodrow Wilson International Center for Scholars",
	"World Resource Institute",
	"Worldwatch Institute",
]

data_main['think_tank'] = ''
count = 0

for i, desc in data_main['witness_desc'].iteritems():
    count += 1
    for tt in think_tanks:
        if tt in str(desc): 
            data_main.at[i, 'think_tank'] = tt
            continue

print "Processed %d rows" % count
data_main.to_csv('ttf_w_tt.csv', encoding="utf-8")
