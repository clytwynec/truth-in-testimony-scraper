# -*- coding: utf-8 -*-
import os
import sys

import requests
from selenium import webdriver
from termcolor import colored

from boto_util import upload_to_s3

start_url = 'http://docs.house.gov/Committee/Search/Home.aspx?Keyword=truth+in+testimony'
next_xpath = '//*[@id="MainContent_btnNext"]'
pages_crawled = 1
ttfs_found = 0


def looks_like_ttf(url):
    """
    Args:
        url: String 
    Returns: Bool
    """
    fn = url.split("/")[-1].lower()
    return ('-ttf-' in fn) or ('disclosure' in fn) or ('truthintest' in fn) or ('-wstate-' in fn and 'sd0' in fn)


def save_ttfs_from_page(driver):
    global ttfs_found

    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        href = elem.get_attribute("href")
        if looks_like_ttf(href):
            # Fetch the content at that URL
            r = requests.get(href, stream=True)

            # Check that content-type is a PDF
            if not r.headers['Content-Type']=='application/pdf':
                # If it's not, move on to the next link
                continue

            meeting_elem = elem.find_element_by_xpath('../ancestor::li[@class="search"]')
            info = {'orig_form_url': r.url}
            info['meeting_title'] = meeting_elem.find_element_by_xpath('./h3/a').text
            info['meeting_id'] = meeting_elem.find_element_by_xpath('./h3/small').text
            info['meeting_status'] =  meeting_elem.find_element_by_xpath('./ul/small').text
            info['meeting_details'] = meeting_elem.find_element_by_xpath('./ul').text.split('\n')[0]

            ttfs_found += 1
            file_name = r.url.split("/")[-1]
            
            if keep_data:
                # Upload TTF to S3
                print colored('********* Uploading to S3: ' + file_name, 'cyan')        
                info['s3_form_url'] = upload_to_s3(r.content, '03142018' + '/' + file_name, 'ttf-forms')
                
                # Store metadata in google sheets
                print colored('********* Saving metadata for: ' + file_name, 'cyan')        
                # TODO
            else:
                print colored('********* Would upload to S3: ' + file_name, 'yellow')        
                print colored('********* Would save metadata for: ' + file_name, 'yellow')        


def print_crawl_summary():
    print 'Done crawling.\n'
    print '____CRAWL SUMMARY____'
    print str(pages_crawled) + ' pages crawled'
    print str(ttfs_found) + ' TTFs found\n'


def crawl_it():
    global pages_crawled

    driver = webdriver.Firefox()
    driver.get(start_url)

    while True:
        # Save TTFs on current page
        save_ttfs_from_page(driver)
        if short_run and pages_crawled == 3:
            break
        try:
            next_btn = driver.find_element_by_xpath(next_xpath)
            next_btn.click()
            print colored('Clicked next button, count ' + str(pages_crawled), 'white', 'on_cyan')
            pages_crawled += 1
        except:
            break

    print_crawl_summary()
    driver.close()

keep_data = '-d' not in sys.argv[1:]
short_run = '-q' in sys.argv[1:]
crawl_it()
