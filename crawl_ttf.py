# -*- coding: utf-8 -*-
import argparse
import csv
import datetime as dt
import hashlib
import os
import time

import requests
from requests.exceptions import ConnectionError
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from termcolor import colored

from boto_util import upload_to_s3


#############################################################################
# GLOBAL VARS
sheet_columns = [
    'uid',
    'event_id',
    'event_url',
    'event_title',
    'event_committees',
    'event_datetime',
    'event_location',
    'witness_name',
    'witness_desc',
    'ttf_url',
    'ttf_url_s3',
]

ttfs_found = 0
events_found = 0
witnesses_found = 0


#############################################################################
# TTF FILES & DATA STORAGE

# OUTDATED
# def looks_like_ttf(url):
#     """
#     Args:
#         url: String 
#     Returns: Bool
#     """
#     fn = url.split("/")[-1].lower()
#     return ('-ttf-' in fn) or ('disclosure' in fn) or ('truthintest' in fn) or ('if17-wstate' in fn and 'sd002' in fn)

def calc_uid(hashable):
    h = hashlib.new('ripemd160')
    h.update(hashable)
    return h.hexdigest()

def save_csv_row(sheetname, row):
    with open(sheetname, mode='a') as ttf_records:
        ttf_records_writer = csv.writer(ttf_records)
        encoded = [str(r.encode('utf8')) if r else r for r in row]
        ttf_records_writer.writerow(encoded)

def save_ttf_files(event):
    global ttfs_found

    for idx, witness in enumerate(event['witnesses']):
        if not witness['ttf_url']:
            continue

        ttfs_found += 1 

        # Fetch the content at that URL
        try:
            r = requests.get(witness['ttf_url'], stream=True)
        except ConnectionError as err:
            print colored("Error fetching TTF file at %s. \n\t %s" % (witness['ttf_url'], err), 'red')
            continue

        # Check that content-type is a PDF
        if not r.headers['Content-Type']=='application/pdf':
            # If it's not, move on to the next link
            continue

        file_name = witness['ttf_url'].split("/")[-1]
        
        if keep_data:
            # Upload TTF to S3
            print colored('********* Uploading to S3: ' + file_name, 'cyan')
            new_url = upload_to_s3(r.content, sheet_name + '/' + file_name, 'ttf-forms')        
            event['witnesses'][idx]['ttf_url_s3'] = new_url
        else:
            print colored('********* Would upload to s3: ' + file_name, 'grey')   
            event['witnesses'][idx]['ttf_url_s3'] = 'mock_url_' + str(idx)    

    return event


def save_ttf_info(info):
    if keep_data:
        save_csv_row(sheet_name, [info[col] for col in sheet_columns])
    else: 
        print colored('********* Would save metadata for: ' + info['witness_name'] + ' ' + info['event_id'], 'grey')        



#############################################################################
# DAYS

def day_url(daystr):
    return "http://docs.house.gov/Committee/Calendar/ByDay.aspx?DayID=" + daystr


def get_daystr(y, m, d):
    return dt.date(y, m, d).strftime("%m%d%Y")


def get_next_date(tries_left=3):
    global cur_day, cur_month, cur_year
    if cur_day > 30:
        if cur_month > 11:
            return None
        else:
            cur_month += 1
            cur_day = 1
    else:
        cur_day += 1

    try:
        return get_daystr(cur_year, cur_month, cur_day)
    except:
        if not tries_left:
            raise
        return get_next_date(tries_left - 1)


def fetch_day_sched(driver, date, retries_left=5):
    """
    Goes to docs.house.gov schedule for date and collects info for each meeting.

    Args:
        driver: selenium driver instance
        date: a date (in format mmddyyy)
    Returns: List of meetings_urls.
    """
    try: 
        url = day_url(date)
        driver.get(url)
        elems = get_elems(driver, "//a[@href]") or []
        hrefs = [elem.get_attribute("href") for elem in elems]
        return [href for href in hrefs if looks_like_event(href)]
    except WebDriverException:
        if retries_left:
            print 'Timedout fetching day ' + date + ', retrying'
            return fetch_day_sched(driver, date, retries_left - 1)
        else:
            raise


#############################################################################
# MEETINGS

def looks_like_event(url):
    """
    Args:
        url: String 
    Returns: Bool
    """
    return 'docs.house.gov/Committee/Calendar/ByEvent.aspx?EventID=' in url



def fetch_events(driver, event_urls):
    """
    Args:
        driver: selenium driver instance
        events_hrefs: results of fetch_day_sched

    Returns: list of events

    Each event is a dict like the following:
    {
        'info': {
            'event_id': '',
            'event_title': '',
            'event_committees': [],
            'event_datetime': '',
            'event_location': ''
        },
        'witnesses': [
            {
                'ttf_url': '',
                'witness_name': '',
                'witness_desc': '',
                'ttf_url_s3': '' !!!added by save_ttf_files function
            }, ...
        ],
    }
    """
    events = []
    for url in event_urls:
        driver.get(url)
        event = {
            'info': {
                'event_id': url.split("=")[1],
                'event_url': url,
                'event_title': get_elem_text(get_first_elem(driver, '//*[@id="previewPanel"]/div[@class="well"]/h1')),
                'event_committees': get_elem_text(get_first_elem(driver, '//*[@id="previewPanel"]/div[@class="well"]/h1/small')),
                'event_datetime': get_elem_text(get_first_elem(driver, '//*[@id="previewPanel"]/div[@class="meeting-date"]')),
                'event_location': get_elem_text(get_first_elem(driver, '//*[@id="previewPanel"]/*[@class="location"]')),
            },
            'witnesses': [],
        }
        
        witnesses = get_elems(driver,'//*[@id="previewPanel"]/div[@class="witnessPanel"]')
        
        print 'found ' + str(len(witnesses)) + ' witnesses'

        for witness in witnesses:
            witness_name = get_elem_text(get_first_elem(witness, './p/strong'))
            
            if witness_name == 'ERROR':
                continue

            witness_docs = get_elems(witness, ".//li")

            def is_ttf(li):
                text = li.text.lower()
                if (
                    "truth in testimony" in text
                    or "disclosure" in text
                    or "related witness support document" in text
                ):
                    return True
                else:
                    return False

            ttf_docs = [li for li in witness_docs if is_ttf(li)]
            witness_link = None
            witness_href = None
            if len(ttf_docs):
                witness_link = get_first_elem(ttf_docs[0], ".//a[@href]")
            if witness_link:
                witness_href = witness_link.get_attribute("href")

            event['witnesses'].append({
                'witness_name': witness_name,
                'witness_desc': get_elem_text(get_first_elem(witness, './p/small')),
                'ttf_url': witness_href,
                'ttf_url_s3': None,
            })

        events.append(event)

    return events

#############################################################################
# SELENIUM HELPERS

def get_elem_text(el):
    try:  
        return el.text
    except:
        return 'ERROR'

def get_elems(driver, xpath, retry=3):
    results = []
    while retry:
        try:
            results = driver.find_elements_by_xpath(xpath)
            break
        except Exception as err:
            retry-=1
            if not retry:
                print colored('Error fetching elements: ' + err, 'yellow')
            break
    return results


def get_first_elem(driver, xpath, retry=3):
    results = None
    while retry:
        try:
            results = driver.find_element_by_xpath(xpath)
            break
        except Exception as err:
            retry-=1
            if not retry:
                print colored('Error fetching element: ' + err, 'yellow')
            break
    return results


#############################################################################
# MAIN

def print_crawl_summary():
    print '____CRAWL SUMMARY____'
    print 'Crawled from %d-%d-%d' % (args.cur_month, args.cur_day, cur_year) + 'through %d-%d-%d' % (cur_month, cur_day, cur_year)
    print str(events_found) + ' events found'
    print str(ttfs_found) + ' TTFs found\n'  



def crawl_it():
    global witnesses_found
    global events_found


    try:
        if keep_data:
            save_csv_row(sheet_name, sheet_columns)

        driver = webdriver.Firefox()
        next_date = get_daystr(cur_year, cur_month, cur_day)

        # Go through each day of the year specified in command line (1st arg)
        while next_date:
            # Go to the schedule page on docs.house.gov for the that day,
            # and get a list with a url for each hearing scheduled that day
            print colored('FETCHING events URLS for day: ' + next_date, 'white')
            events_urls = fetch_day_sched(driver, next_date)

            # Take that list of urls and visit each event page
            # Grab the info about that event (see fetch_events function)
            # It will include info about each person that testified,
            # including a link to their TTF form if found
            print colored('FETCHING event INFO for day: ' + next_date, 'white')
            events = fetch_events(driver, events_urls)
            events_found += len(events)

            # For each of those events, for each witness,
            # ave the TTF form if it was found, and save the
            # metadata about that witness/ttf form
            for event in events:
                print colored('PROCESSING event: ' + event['info']['event_id'], 'white')
                updated_event = save_ttf_files(event)
                for witness in updated_event['witnesses']:
                    print colored('PROCESSING witness: ' + witness['witness_name'], 'white')
                    witnesses_found += 1
                    uid_hashable = (event['info']['event_id'] + witness['witness_name'] + witness['witness_desc']).encode('utf-8', 'replace')
                    info = {
                        'uid': calc_uid(uid_hashable),
                        'date_retrieved': dt.date.today(),
                    }
                    info.update(event['info'])
                    info.update(witness)
                    save_ttf_info(info)

            next_date = get_next_date()

    finally:
        driver.close()
        print_crawl_summary()
 

#############################################################################
# COMMAND LINE

parser = argparse.ArgumentParser(description='''
            Crawl docs.house.gov looking for TTFs.
            e.g. `python crawl_ttf.py -y 2017 -m 3 -s 2017_03_ttfs`
            will crawl for TTFs from meetings from March 2017 until the end of 2017
            and store them in a CSV titled 2017_03_ttfs.
            
            Specifying the file name and month/day can let you restart the crawl from the point of failure
            in case of a network issue or some other transient error.
        ''')

parser.add_argument('--dryrun', dest='keep_data', action='store_false', default=True,
                    help='run crawler without storing results')
parser.add_argument('--sheetname', '-s', dest='sheet_name', action='store', default=0,
                    help='Name of sheet to store data to. Will add to an existing sheet if a matching one is found, else creates a new sheet.')
parser.add_argument('--year', '-y', dest='cur_year', action='store', required=True,
                    help='year to crawl', type=int)
parser.add_argument('--month', '-m', dest='cur_month', action='store', default=1, type=int,
                    help='month to start from (as integer, e.g. 4 for April), Default: start in January')
parser.add_argument('--day', '-d', dest='cur_day', action='store', default=1, type=int,
                    help='day to start from (as integer), Default: start on first day of month')

args = parser.parse_args()

cur_month = args.cur_month
cur_day = args.cur_day
cur_year = args.cur_year
keep_data = args.keep_data
sheet_name = args.sheet_name or (str(cur_year) + '_crawled_at_'+ str(dt.datetime.utcnow()).replace(':', '-').replace(' ', '-'))

crawl_it()
