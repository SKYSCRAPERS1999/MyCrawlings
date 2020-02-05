# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time

import pymongo

from stackoverflow.items import QuestionItem, AnswerItem, QuestionFullItem


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.date = time.strftime('%Y-%m-%d', time.localtime())

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[QuestionItem.collection].create_index([('q_id', pymongo.ASCENDING)])
        self.db[AnswerItem.collection].create_index([('a_id', pymongo.ASCENDING)])

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, QuestionItem) or isinstance(item, QuestionFullItem):
            self.db[item.collection].update({'q_id': item.get('q_id')}, {'$set': item}, True)
        elif isinstance(item, AnswerItem):
            self.db[item.collection].update({'a_id': item.get('a_id')}, {'$set': item}, True)
        return item
