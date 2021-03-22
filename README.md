### Truth in Testimony Form Crawler

Crawls docs.house.gov and grabs TTF files.
Puts files into S3 and stores metadata in a CSV.

## Background

![Story Image](https://stine-stuff.s3.amazonaws.com/images/ttf_post_img.original.png)

This code was used in an investigative journalism project looking at the implementation and effectiveness of the "Truth in Testimony" rule in the U.S. House of Representatives which requires those who testify before the House to disclose any foreign funding related to the hearing at which they testify. The final product includes a [4000+ word story](http://investigativereportingworkshop.org/investigation/foreign-influence/), [a database of the testimonies and an description of our process](https://investigativereportingworkshop.org/news/foreign-influence-how-we-built-the-database-of-expert-testimony/), and a ["by the numbers" overview](https://investigativereportingworkshop.org/news/foreign-influence-house-transparency-in-numbers/) of our findings.
This code is not gerneralized, but kept available for transparency and as a resource for others interested in similar projects.

## Installation

`pip install -r requirements.txt`

Set up AWS credentials to save the files to a bucket. See https://github.com/boto/boto3#quick-start.

## Usage

To see options, use `python crawl_ttf.py -h`

![Scraper Demo Gif](ttf_crawler_gif.gif)


## Post-crawl processing

#### Concatenating the years

`merge_csv.py` was used to combine the crawls from separate years into one file.

#### Removing duplicates
`drop_duplicates.py` was used to remove duplicate rows from CSV file by UID.

#### Truth in Testimony forms

After crawling, we went through the Truth in Testimony forms manually and recorded the diclosed foreign funding. I used `merge_data.py` to merge that data with the originally crawled data.

#### Identifying think tanks

`id_think_tanks.py` creates a copy of the data with a column `think_tank` that contains the name of the think tank named in the `witness_desc` field. This works off of a list of known think tanks and isn't necessarily complete.