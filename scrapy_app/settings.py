from os import path
import logging
import urllib.parse

SPIDER_MODULES = ['scrapy_app.spiders']
PROJECT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
RESULTS_DIR = path.join(PROJECT_DIR, 'results')
LOG_DIR = path.join(PROJECT_DIR, 'etc')
INPUT_FILE_PATH = path.join(PROJECT_DIR, 'ml.txt')
INPUT_FILE_DIR = path.join(PROJECT_DIR, 'input')
DOWNLOAD_DELAY = 3
DATA_FILE_PATH = path.join(INPUT_FILE_DIR, 'data.yaml')

MAX_RESULTS_PER_QUERY = 100

#Avoid <urlopen error timed out>
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""


ITEM_PIPELINES = {
    #'scrapy_app.pipelines.DetectLanguagePipeline': 100,
    'scrapy_app.pipelines.Format': 300,
    #'scrapy_app.pipelines.CSVPipeline': 700,
    'scrapy_app.pipelines.JsonPipeline': 800,
    'scrapy_app.pipelines.MongoPipeline': 950,
    'scrapy_app.pipelines.DuplicateFinderPipeline': 150,
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/56.0.2924.87 Safari/537.36'

from scrapy.utils.log import configure_logging as configure_scrapy_logging
from scrapy_app.utils import configure_file_logging
configure_scrapy_logging(install_root_handler=False)
LOG_LEVEL = 'DEBUG'  # for scrapy console
configure_file_logging(log_dir=LOG_DIR, file_name='log.txt', mode='w', level=logging.DEBUG)

# MongoDB config Details
'''
    These settings works with the docker compose file. 
    Need to change these if we host MongoDB in a seperate location

'''
MONGODB_SERVER = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_DATABASE = 'kimo_data'
MONGODB_COLLECTION = 'medium'
MONGODB_USER = 'kimo_1'
MONGODB_PASS = 'OoFV4Mdw8DpJGXrP'
MONGODB_URI = 'mongodb+srv://{}:{}@kimo0-0tlxa.mongodb.net/test?retryWrites=true&w=majority'.format(MONGODB_USER, MONGODB_PASS)

