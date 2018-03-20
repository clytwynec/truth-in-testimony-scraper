# -*- coding: utf-8 -*-
import google_sheets_util as sheets
import time

sheet_name = '2017_ttfs_with_uids'
row_count = sheets.get_row_count(sheet_name)

for row_idx in range(50, row_count + 2):
	row = sheets.get_row(sheet_name, row_idx)
	event_id = row[1]
	witness_name = row[6] 
	witness_desc = '' 
	try:
		witness_desc = row[7]
	except IndexError:
		pass

	uid = sheets.calc_uid(event_id + witness_name + witness_desc)
	print row_idx, uid
	sheets.update_cell(sheet_name, 'A' + str(row_idx), uid)
	time.sleep(5) # wait a second for each call plus 1

