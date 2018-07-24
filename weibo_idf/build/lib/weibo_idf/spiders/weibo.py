# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import json, pymongo, time, re, random
from weibo_idf.items import TextItem

class WeiboSpider(Spider):
    name = 'weibo_idf'
    allowed_domains = ['weibo.cn']
    start_urls = ['http://weibo.cn/']
    
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
        
    start_users = [
    '1797054534', '2509414473', '2611478681', '5861859392', '2011086863', '5127716917', '1259110474', '5850775634', '1886437464',
    '3187474530', '2191982701', '1940562032', '5874450550', '1337925752', '2081079420', '5664530558', '3493173952', '1202806915',
    '1864507535', '2032640064', '5585682587', '3083673764', '5342109866', '5878685868', '5728706733', '2103050415', '5876752562',
    '3138085045', '5775974583', '1879400644', '2417139911', '5836619975', '5353816265', '5219508427', '1766613205', '2480158031',
    '5660754163', '2456764664', '3637354755', '1940087047', '5508473104', '1004454162', '2930327837', '1874608417', '5379621155',
    '1720664360', '2714280233', '3769073964', '5624119596', '2754904375', '5710151998', '5331042630', '5748179271', '2146132305',
    '2313896275', '3193618787', '5743059299', '1742930277', '5310538088', '1794474362', '2798510462', '3480076671', '5678653833',
    '5743657357', '5460191980', '1734164880', '5876988653', '5678031258', '5860163996', '1496924574', '5878970110', '1679704482',
    '1142210982', '3628925351', '1196397981', '1747485107', '5675893172', '5438521785', '2192269762', '1992614343', '5878686155',
    '2407186895', '5559116241', '2528477652', '1295950295', '5038203354', '3659276765', '2126733792', '5878350307', '2761179623',
    '5484511719', '5825708520', '1578230251', '5878686190', '5810946551', '3833070073', '1795047931', '5855789570', '3580125714',
    '5709578773', '5236539926', '2907633071', '1709244961', '5405450788', '3251257895', '5054538290', '2713199161', '5698445883',
    '1784537661', '3195290182', '1824506454', '5738766939', '5565915740', '5336031840', '5098775138', '5685568105', '1774289524',
    '2932662914', '5433223957', '2680044311', '1111523983', '5067889432', '5878686362', '2844992161', '3878314663', '1766548141',
    '5763269297', '5878383287', '5235499706', '5876375670', '5866447563', '5129945819', '1704116960', '1929380581', '1223762662',
    '1193476843', '2899591923', '5162099453', '5072151301', '5385741066', '5411455765', '2685535005', '2297905950', '1216766752',
    '5838668577', '5359133478', '3077460103', '5577802539', '5862392623', '1786700611', '1259258694', '1845191497', '1731838797',
    '1740301135', '2816074584', '1217733467', '5345035105', '5050827618', '5486257001', '5767857005', '2050605943', '5733778298',
    '1914725244', '5872583558', '5604377483', '1253491601', '5554922386', '3170223002', '5662737311', '3217179555', '1538163622',
    '5304533928', '5644198830', '1896650227', '5298774966', '2795873213', '1834378177', '5769651141', '2656256971', '5876433869',
    '1826792401', '3002246100', '3082519511', '5780366296', '5704696797', '5204108258', '2090615793', '1739746131', '1378010100',
    '5741331445', '2376442895', '3638486041', '5781365789', '1827234850', '5703214121', '1855398955', '1227908142', '5703820334',
    ]
    
    finished = set()
    
    def start_requests(self):       
        random.shuffle(self.start_users)
        for uid in self.start_users[:15]:
            yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            
    def parse_user(self, response):
        """
        解析用户信息
        :param response: Response对象
        """
           
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            uid = user_info.get('id')
                    
            # 微博
            self.logger.info("parsing weibos of {}".format(uid))
            yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                          meta={'page': 1, 'uid': uid})  
            
            if user_info.get('followers_count') != None:
                # 关注
                self.logger.info("parsing followings of {}".format(uid))
                yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows,
                              meta={'page': 1, 'uid': uid})                
        
            self.finished.add(uid)
            
    def parse_follows(self, response):
        """
        解析用户关注
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and result.get('data').get('cards')[-1].get(
            'card_group'):
            # 解析用户
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    uid = follow.get('user').get('id')
                    if uid not in self.finished:
                        yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
                            
            uid = response.meta.get('uid')
            # 下一页关注
            page = response.meta.get('page') + 1
            yield Request(self.follow_url.format(uid=uid, page=page),
                          callback=self.parse_follows, meta={'page': page, 'uid': uid})
            
    def parse_weibos(self, response):
        """
        解析微博列表
        :param response: Response对象
        """
        result = json.loads(response.text)
        
        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                    
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = TextItem()
                    field_map = {
                        'id': 'id', 'text': 'text'
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    if mblog.get('retweeted_status') != None:
                        retweet = mblog.get('retweeted_status')
                        if retweet.get('text') != None:
                            weibo_item['text'] += retweet.get('text')
                    
                    yield weibo_item
                    
            # 下一页微博
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page})
                
       