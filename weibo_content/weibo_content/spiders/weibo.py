# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import json, pymongo, time, re
from weibo_content.items import WeiboItem, TextItem
from weibo_content.idmap import user_id_map

week = [ time.strftime('%Y-%m-%d', time.localtime(time.time() - x * 24 * 60 * 60)) for x in range(8) ] 

class WeiboSpider(Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    start_urls = ['http://weibo.cn/']
    
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    
    mongo_uri = 'mongodb://impulse:njuacmicpc@120.79.139.239/weibo'
    spider_client = pymongo.MongoClient(host=mongo_uri, port=27017)
    
    db = spider_client['weibo']
    collection = db['users']
    collection_weibo = db['weibos']
    start_users = []
    text_re1 = re.compile('"text":[ ]+"(.*)"')
    text_re2 = re.compile('"longTextContent":[ ]+"(.*)"')
    
    #date = time.strftime('%Y-%m-%d', time.localtime())
    #ldate = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60))
    #lldate = time.strftime('%Y-%m-%d', time.localtime(time.time() - 2 * 24 * 60 * 60))
    
    def start_requests(self):
        
        time_re = re.compile('|'.join(week))
        deletes = self.collection_weibo.find({'created_date': {'$not': time_re}})
        
        del_id = []
        for dele in deletes:
            if dele.get('id') != None:
                del_id.append(dele.get('id'))
        for id in del_id:
            self.collection_weibo.delete_one({'id': str(id)})
                    
        results = self.collection.find({}, {'id':1})  
        for result in results:
            if result['id'] != None:
                self.start_users.append(str(result['id']))
        self.logger.critical('length of start_users: {}'.format(len(self.start_users)))

        self.spider_client.close()
        
        for cnt, uid in enumerate(self.start_users):
            self.logger.critical('parsing the {}th user: {}'.format(cnt, uid))
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                          meta={'page': 1, 'uid': uid})                
    
    def parse_weibos(self, response):
        """
        解析微博列表
        :param response: Response对象
        """
        result = json.loads(response.text)
        uid = response.meta.get('uid')

        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                    
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count', 'created_at': 'created_at', 'source': 'source', 'text': 'text'
                        ,'avatar': 'profile_image_url', 'name': 'screen_name'
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    if mblog.get('retweeted_status') != None:
                        retweet = mblog.get('retweeted_status')
                        if retweet.get('text') != None:
                            weibo_item['text'] += retweet.get('text')
                    weibo_item['user'] = response.meta.get('uid')
                    ## cluster_class
                    weibo_item['cluster_class'] = user_id_map[int(weibo_item['id'])]
                    
                    yield weibo_item
                    
                    if weibo.get('scheme') != None:
                        if len(str(weibo_item['text'])) >= 135 and re.search('全文', weibo_item['text']) != None:
                            yield Request(weibo.get('scheme'), callback=self.parse_fulltext,
                              meta={'id': weibo_item['id']})                       
                    
                    if weibo_item.get('created_date') != None and weibo_item.get('created_date') not in week:
                        self.logger.critical('finish parsing user {}'.format(uid))
                        return
                    
            # 下一页微博
            page = response.meta.get('page') + 1
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page})
            
    def parse_fulltext(self, response):
        self.logger.critical("getting fulltext\n")
        
        fulltext_item = TextItem()
        fulltext_item['id'] = response.meta.get('id')
        elements = response.xpath(".").re(self.text_re1)
        extra_element = response.xpath(".").re(self.text_re2)
        fulltext = ""
        if len(elements) > 0:
            fulltext += elements[0]
        
        if len(extra_element) > 0:
            fulltext += extra_element[0]
        elif len(elements) > 1:
            fulltext += elements[1]
            
        fulltext_item['full_text'] = fulltext
        
        if len(fulltext) < 10:
            return
        #self.logger.critical('full_text: {}'.format(fulltext))
        self.logger.critical('isinstance fulltext? : {} is valid?: {}'.format(isinstance(fulltext_item, TextItem), fulltext != None))
    
        yield fulltext_item    