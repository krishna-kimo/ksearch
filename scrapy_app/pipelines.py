from scrapy import signals
from datetime import datetime
import config
import os
import csv
import json
import urllib.parse
from scrapy_app.settings import RESULTS_DIR
from scrapy_app.utils import remove_spaces
from langdetect import detect
from langdetect import detect_langs
from scrapy.exceptions import DropItem
import logging
import pymongo

'''

    TODO:

       Add the Keyword extraction to the pipline
       Add the summary generation to the pipeline

'''


class Format(object):
    def process_item(self, item, spider):
        for key, value in item.items():
            if type(value) == str:
                item[key] = remove_spaces(value)
            if type(value) == set:
                item[key] = list(value)
            if type(value) == datetime:
                item[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        return item


class CSVPipeline(object):
    file = None
    writer = None

    def open_spider(self, spider):
        #file_name = '{}_items_{}.csv'.format(spider.name, datetime.utcnow().date())
        #file_name = 'test_{}_items_{}.csv'.format(spider.name, datetime.utcnow().date())
        file_name = config.get_file_name(config.f_name) + '.csv'
        file_path = os.path.join(RESULTS_DIR, file_name)
        spider.logger.info('Starting export to %s' % file_path)
        try:
            self.file = open(file_path, mode='w', newline='', encoding='utf-8-sig')
            self.writer = csv.writer(self.file)
            self.writer.writerow(spider.csv_fields)
        except PermissionError:
            spider.logger.warning('File is already opened!')

    def process_item(self, item, spider):
        csv_row = []
        for field in spider.csv_fields:
            value = item.get(field)
            if type(value) == list:
                value = ' | '.join(value)
            if item.get(field) in (None, [], ""):
                value = '-'
            csv_row.append(value)

        if self.writer:
            self.writer.writerow(csv_row)
        return item

    def close_spider(self, spider):
        if self.file:
            self.file.close()


class JsonPipeline(object):
    items = {}

    def process_item(self, item, spider):
        self.items.setdefault(item['query'], []).append(dict(item))
        return item

    def close_spider(self, spider):
        #file_name = 'test_{}_items_{}.json'.format(spider.name, datetime.utcnow().date())
        file_name = config.get_file_name(config.f_name) + '.json'
        file_path = os.path.join(RESULTS_DIR, file_name)
        with open(file_path, mode='w', encoding='utf-8') as f:
            json.dump(obj=self.items, fp=f, indent=2, ensure_ascii=False)


class MongoPipeline(object):
    import urllib.parse
    collection_name = 'scrapy_items'

    def __init__(self):
        import logging
        import scrapy_app.settings as db_conf

        self.mongo_uri = db_conf.MONGODB_URI
        self.mongo_db = db_conf.MONGODB_DATABASE
        self.mongo_collection = db_conf.MONGODB_COLLECTION


    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        if self.db[self.mongo_collection].find_one({"article_id" : item["article_id"]}):
            raise DropItem("Item already exists in DB")
        else:
            self.db[self.mongo_collection].insert_one(dict(item))
            return item
    
    def close_spider(self, spider):
        self.client.close()

class DuplicateFinderPipeline(object):
    
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['article_id'] in self.ids_seen:
            raise DropItem("Duplicate Item found with id - {}".format(item['article_id']))
        else:
            self.ids_seen.add(item['article_id'])
            return item

class CheckLanguagePipeline(object):
    pass

