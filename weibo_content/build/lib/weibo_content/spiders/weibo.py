# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import json, pymongo
from weibo_content.items import WeiboItem

class WeiboSpider(Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    start_urls = ['http://weibo.cn/']
    
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    
    spider_client = pymongo.MongoClient(host='localhost', port=27017)
    db = spider_client['weibo']
    collection = db['users']
    start_users = []
    
    def start_requests(self):
        
        results = self.collection.find({}, {'id':1})  
        for result in results:
            if result['id'] != None:
                self.start_users.append(str(result['id']))
        self.logger.info('length of start_users: {}'.format(len(self.start_users)))
        
        for cnt, uid in enumerate(self.start_users):
            self.logger.info('parsing the {}th user: {}'.format(cnt, uid))
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                          meta={'page': 1, 'uid': uid})                
    
    def parse_weibos(self, response):
        """
        解析微博列表
        :param response: Response对象
        """
        result = json.loads(response.text)
        parse_cnt = 0
        
        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                
                parse_cnt += 1
                if (parse_cnt > 10):
                    return
                    
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count', 'picture': 'original_pic', 'pictures': 'pics',
                        'created_at': 'created_at', 'source': 'source', 'text': 'text', 'raw_text': 'raw_text',
                        'thumbnail': 'thumbnail_pic'
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    if mblog.get('retweeted_status') != None:
                        retweet = mblog.get('retweeted_status')
                        if retweet.get('text') != None:
                            weibo_item['text'] += retweet.get('text')
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item
                    
            # 下一页微博
            #uid = response.meta.get('uid')
            #page = response.meta.get('page') + 1
            #yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
            #              meta={'uid': uid, 'page': page})