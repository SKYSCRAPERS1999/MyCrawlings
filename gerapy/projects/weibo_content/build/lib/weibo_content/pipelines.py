# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re, time
import logging
import pymongo
from weibo_content.items import UserItem, WeiboItem, TextItem
from scrapy.exceptions import DropItem

class TimePipeline():
    def process_item(self, item, spider):
        ## must be WeiboItem
        if isinstance(item, WeiboItem):
            now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
            item['crawled_at'] = now
        return item

class WeiboPipeline():
    def parse_time(self, date):
        if re.match('刚刚', date):
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', date):
            hour = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60)) + ' ' + date
        if re.match('\d{2}-\d{2}', date):
            date = time.strftime('%Y-', time.localtime()) + date + ' 00:00'
        return date
    
    def process_item(self, item, spider):
        ## must be WeiboItem 
        if isinstance(item, WeiboItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))
                if item['created_at'].split() != None:
                    item['created_date'] = item['created_at'].split()[0]
            if item.get('pictures'):
                item['pictures'] = [pic.get('url') for pic in item.get('pictures')]
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.date = time.strftime('%Y-%m-%d', time.localtime())
        self.ldate = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60))
        self.lldate = time.strftime('%Y-%m-%d', time.localtime(time.time() - 2 * 24 * 60 * 60))
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[WeiboItem.collection].create_index([('id', pymongo.ASCENDING)])
        
    def close_spider(self, spider):
        self.client.close()
    
    def process_item(self, item, spider):
        ## must be WeiboItem
        if isinstance(item, TextItem):
            #self.logger.info("Setting full text, id = {}".format(item.get('id')))
            self.db[item.collection].update({'id': item.get('id')}, {'$set': {'full_text': item['full_text']} }, False)
        elif isinstance(item, WeiboItem):
            if str(item['created_date']) in [str(self.date), str(self.ldate), str(self.lldate)]:
                self.db[item.collection].update({'id': item.get('id')}, {'$set': item}, True)            
            else:
                raise DropItem('Date not match')
        return item
       