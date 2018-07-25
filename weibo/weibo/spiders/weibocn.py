# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import json, re
from weibo.items import UserItem, UserRelationItem, WeiboItem, OngoingItem, FinishItem
import random, pymongo

class WeibocnSpider(Spider):
    name = 'weibocn'
    allowed_domains = ['weibo.cn']
    start_urls = ['http://weibo.cn/']
    
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
   
    start_users = ["1676368781","2100720873","5616140211","1163218074","1979899604","1249424622","1654657755","6033320519","1319518957","1435160552","2014433131","5384479977","1606612822","1613005690","2812319402","1983026375","5091912327","5938488153","1154814715","1264138094","1560851875","6562202261","5244183267","1593163950","1657765690","2200691290","1196703900","1993298173","2930162624","2291429207","1861477054","3050893364","1660079292","1703827472","2669119637","2354020187","1662313931","1216826604","1687367547","6097181298","1193664907","1669616825","6393953260","1153588720","1190785973","1562273464","1282871591","1645823934","5663133624","2121667213","1974945511","5234375271","5994820427","1410248531","5999363519","1747150823","5703445056","6413999154","1179198244","2272536674","5170186722","1596329427","1371675920","1764753511","1405463773","1908417784","5408006106","1791130774","1245732825","1922275800","1670458304","1977046885","1764452651","1098173713","1320153481","2910812187","2637695114","5991851973","5801666169","1676368781","2100720873","5616140211","1163218074","1979899604","1249424622","1654657755","6033320519","1319518957","1435160552","2014433131","5384479977","1606612822","1613005690","2812319402","1983026375","5091912327","5938488153","1154814715"]
    finish_users = []
    
    #spider_client = pymongo.MongoClient(host='localhost', port=27017)
    spider_client = pymongo.MongoClient(host='120.79.139.239', port=27017)
    db = spider_client['weibo']
    finish_collection = db['finishes']
    ongoing_collection = db['ongoings']
    
    regex = re.compile('(?:谈股|财经|说股|期货|外汇|讲股|论股|看股|港股|美股|理财师|A股|经济政策|短线|炒股|荐股|盈亏|炒股|股利|股海|股民|股票|个股|做空|诱多|诱空|踏空|长空|短空|长多|短多|死多|翻多|翻空|多杀多|扎空|空仓|建仓|满仓|斩仓|减仓|加仓|重仓|清仓|套牢|补仓|仓位|庄家|震仓|追涨|杀跌|止盈|抄底|逃顶|盘整|回档|坐庄|吸筹|对敲|洗盘|散户|中户|坐轿|抬轿|筹码|抢帽子|多头陷阱|空头陷阱|护盘|跳空|开盘价|收盘价|最高价|最低价|成交量|放量|缩量|热门股|冷门股|白马股|黑马股|龙头股|阴跌|换手率|现手|平开|低开|高开|内盘|外盘|均价|浮筹|市盈率|含权|回购|基本面分析|量比|每股|收益|市净率|探底|填权|停牌|退市)')    
  
    nregex = re.compile('(?:公司|企业|CEO|基金会|大学|学院|政府)')
    
    output_info = True
    finish_ID = set()
    ongoing_ID = set()
    
    def start_requests(self):
        results = self.ongoing_collection.find({}, {'oid':1})  
        for result in results:
            cur = str(result['oid'])
            if cur != None:
                self.start_users.append(cur)
                self.ongoing_ID.add(cur)
        self.logger.info('length of start_users: {}'.format(len(self.start_users)))
        
        results = self.finish_collection.find({}, {'fid':1})  
        for result in results:
            cur = str(result['fid'])
            if cur != None:
                self.finish_users.append(cur)
                self.finish_ID.add(cur)
        self.logger.info('length of finish_users: {}'.format(len(self.finish_users)))        
        
        random.shuffle(self.start_users)
        for uid in self.start_users:
            yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            
    def validify_user(self, user_info):
        if user_info.get('id') == None:
            return False
        #uid = user_info.get('id')   
        if user_info.get('description') == None or user_info.get('verified_reason') == None or user_info.get('verified_type') == None:
            return False
        if user_info.get('verified_type') == -1:
            return False
        if re.search(self.regex, user_info.get('description')) == None or re.search(self.nregex, user_info.get('description')) != None:
            return False
        return True
        
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
            
            ## if is garbage, then return
            if str(uid) in self.finish_ID:
                return
            
            self.logger.info("In uid {}: ongoing: {}".format(uid, str(uid) in self.ongoing_ID))                            
            self.logger.info(response)
            
            if str(uid) not in self.ongoing_ID and self.validify_user(user_info):
                self.logger.info("Create Item !!!\nIn uid {}".format(uid))
                
                user_item = UserItem()
            
                field_map = {
                    'id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                    'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                    'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                    'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
                }
                
                for field, attr in field_map.items():
                    user_item[field] = user_info.get(attr)
                
                self.output_info = True
                
                ## process -> add into queue
                self.ongoing_ID.add(str(uid))
                self.ongoing_collection.insert_one({'oid': str(uid)})
                
                yield user_item               
            
            if (len(self.ongoing_ID) % 2 == 0 or len(self.finish_ID) % 2 == 0) and self.output_info == True:
                self.output_info = False
                self.logger.info('ongoing: {}'.format(len(self.ongoing_ID)))
                self.logger.info('finish: {}'.format(len(self.finish_ID)))
                    
            # 微博
            #yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
            #              meta={'page': 1, 'uid': uid})         
            if user_info.get('followers_count') != None and user_info.get('follow_count') != None and user_info.get('followers_count') > 3 * user_info.get('follow_count'):
                # 关注
                self.logger.info("parsing followings of {}".format(uid))
                yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows,
                              meta={'page': 1, 'uid': uid})
                # 粉丝
                self.logger.info("parsing fans of {}".format(uid))
                yield Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans,
                         meta={'page': 1, 'uid': uid})
                
            ## end process -> remove from queue
            if str(uid) in self.ongoing_ID:
                self.ongoing_ID.discard(str(uid))
                self.ongoing_collection.delete_many({'oid': str(uid)})
                self.finish_ID.add(str(uid))
                self.finish_collection.insert_one({'fid': str(uid)})
                
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
                    if uid not in self.finish_ID:
                        yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
                            
            uid = response.meta.get('uid')
            # 关注列表
            ## not in use yet!!!
            # user_relation_item = UserRelationItem()
            # follows = [{'id': follow.get('user').get('id'), 'name': follow.get('user').get('screen_name')} for follow in
            #            follows]
            # user_relation_item['id'] = uid
            # user_relation_item['follows'] = follows
            # user_relation_item['fans'] = []
            # yield user_relation_item
            
            # 下一页关注
            page = response.meta.get('page') + 1
            yield Request(self.follow_url.format(uid=uid, page=page),
                          callback=self.parse_follows, meta={'page': page, 'uid': uid})
    
    def parse_fans(self, response):
        """
        解析用户粉丝
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and result.get('data').get('cards')[-1].get(
            'card_group'):
            # 解析用户
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('id')
                    yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            
            uid = response.meta.get('uid')
            # 粉丝列表
            # not in use yet!!
            
            # user_relation_item = UserRelationItem()
            # fans = [{'id': fan.get('user').get('id'), 'name': fan.get('user').get('screen_name')} for fan in
            #         fans]
            # user_relation_item['id'] = uid
            # user_relation_item['fans'] = fans
            # user_relation_item['follows'] = []
            # yield user_relation_item
            
            # 下一页粉丝
            page = response.meta.get('page') + 1
            yield Request(self.fan_url.format(uid=uid, page=page),
                          callback=self.parse_fans, meta={'page': page, 'uid': uid})
    
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
                        'thumbnail': 'thumbnail_pic',
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item
                    
            ## only one page
            return
            # no 下一页微博
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            yield Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page})
