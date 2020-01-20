import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import config
from scrapy_app.spiders.spider import MediumSpider

parser = argparse.ArgumentParser()
parser.add_argument('--file_name', help='OutPut File Name', default='scraped')

args = parser.parse_args()

config.f_name = args.file_name

process = CrawlerProcess(get_project_settings())
process.crawl(MediumSpider)
process.start()
