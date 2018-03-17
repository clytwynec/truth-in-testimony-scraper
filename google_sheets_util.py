# -*- coding: utf-8 -*-
"""
See http://gspread.readthedocs.io/en/latest/
Good tutorial: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]

creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)


def get_or_create_worksheet(sheet_name, sheet_columns):
    try:
        client.open("ttf_crawler_records").worksheet(sheet_name)
    except:
        client.open("ttf_crawler_records").add_worksheet(sheet_name, 0, 0)
        append_row(sheet_name, sheet_columns)


def append_row(sheet_name, data):
    client.open("ttf_crawler_records").worksheet(sheet_name).append_row(data)
