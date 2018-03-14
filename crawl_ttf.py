# -*- coding: utf-8 -*-
import os

import boto3
from selenium import webdriver
from termcolor import colored


start_url = 'http://docs.house.gov/Committee/Search/Home.aspx?Keyword=truth+in+testimony'
next_xpath = '//*[@id="MainContent_btnNext"]'


def upload_to_s3(file_data, file_name, bucket_name):
    print file_name, bucket_name
    # Create an S3 client
    s3 = boto3.resource('s3')
    s3Obj = s3.Object(bucket_name, file_name)

    s3Obj.put(
        ACL='public-read',
        Body=file_data,
        ContentType='application/pdf',
    )


def is_ttf(url):
    """
    Args:
        url: String 
    Returns: Bool
    """
    fn = url("/")[-1].lower
    return ('-ttf-' in fn) or ('disclosure' in fn) or ('truthintest' in fn) or ('-wstate-' in fn and 'sd0' in fn)


def save_ttfs_from_page(response):
    if is_ttf(file_name) and response.headers['Content-Type']=='application/pdf':
        split_url = response.url.split("/")
        # page = split_url[-1]
        domain = split_url[2]
        # committee_code = split_url[4].upper()

        print colored('********* Uploading to S3: ' + file_name, 'cyan')
        # upload_to_s3(response.body, committee_code + '/' + file_name, 'ttf-forms')
        upload_to_s3(response.body, '03142018' + '/' + file_name, 'ttf-forms')


def crawl_it():
    driver = webdriver.Firefox()
    driver.get(start_url)

    while True:
        next_btn = driver.find_element_by_xpath(next_xpath)
        try:
            import ipdb; ipdb.set_trace()
            next_btn.click()
        except:
            break

    driver.close()


crawl_it()
