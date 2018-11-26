### TTF_CRAWLER

Crawls docs.house.gov and grabs TTF files.
Puts files into S3 and stores info in a CSV.


## Installation

`pip install -r requirements.txt`

Set up AWS credentials to save the files to a bucket. See https://github.com/boto/boto3#quick-start.

## Usage

To see options, use `python crawl_ttf.py -h`


## Post-crawl processing

#### Concatenating the years

`merge_csv.py` was used to combine the crawls from separate years into one file.

#### Truth in Testimony forms

After crawling, we went through the Truth in Testimony forms manually and recorded the diclosed foreign funding. I used `merge_data.py` to merge that data with the originally crawled data.

#### Identifying think tanks

`id_think_tanks.py` creates a copy of the data with a column `think_tank` that contains the name of the think tank named in the `witness_desc` field. This works off of a list of known think tanks and isn't necessarily complete.