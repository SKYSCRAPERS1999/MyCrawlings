# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import json, re
from weibo.items import UserItem, UserRelationItem, WeiboItem

class WeibocnSpider(Spider):
    name = 'weibocn'
    allowed_domains = ['weibo.cn']
    start_urls = ['http://weibo.cn/']
    
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    start_users = ['1896820725', '1216826604', '1613005690', '2014433131', '1645823934', '1653661844', '1364334665', '2144596567']
    
    regex = re.compile('(?:谈股|说股|讲股|论股|看股|港股|美股|财经|期货|基金|外汇|理财师|A股|经济政策|短线|炒股|荐股|盈亏|炒股|股利|股海|股民|股票|个股|做空|诱多|诱空|踏空|长空|短空|长多|短多|死多|翻多|翻空|多杀多|扎空|空仓|建仓|满仓|斩仓|减仓|加仓|重仓|清仓|套牢|补仓|仓位|庄家|震仓|追涨|杀跌|止盈|抄底|逃顶|盘整|反弹|回档|坐庄|吸筹|对敲|打压|洗盘|散户|中户|坐轿|主力|抬轿|筹码|抢帽子|多头陷阱|空头陷阱|护盘|跳空|开盘价|收盘价|最高价|最低价|成交量|放量|缩量|热门股|冷门股|白马股|黑马股|龙头股|阴跌|换手率|现手|平开|低开|高开|内盘|外盘|均价|浮筹|市盈率|含权|回购|基本面分析|量比|每股|收益|市净率|探底|填权|停牌|退市)')    
    nregex = re.compile('(?:公司|企业|CEO)')
    
    def start_requests(self):
        for uid in self.start_users:
            yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
    
    def validify_user(self, user_info):
        if user_info.get('description') == None or user_info.get('verified_reason') == None or user_info.get('verified_type') == None:
            return False
        if user_info.get('verified_type') == -1:
            return False
        if re.search(self.regex, user_info.get('description')) == None:
            return False
        if re.search(self.nregex, user_info.get('description')) != None:
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
            user_item = UserItem()
            field_map = {
                'id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
            }         
            
            if not self.validify_user(user_info):
                return
            
            for field, attr in field_map.items():
                user_item[field] = user_info.get(attr)
            yield user_item
            
            uid = user_info.get('id')
            # 微博
            #yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
            #              meta={'page': 1, 'uid': uid})
            
            # 关注
            yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows,
                          meta={'page': 1, 'uid': uid})
            # 粉丝
            #yield Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans,
            #              meta={'page': 1, 'uid': uid})
          
    
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
                    yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            
            uid = response.meta.get('uid')
            # 关注列表
            user_relation_item = UserRelationItem()
            follows = [{'id': follow.get('user').get('id'), 'name': follow.get('user').get('screen_name')} for follow in
                       follows]
            user_relation_item['id'] = uid
            user_relation_item['follows'] = follows
            user_relation_item['fans'] = []
            yield user_relation_item
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
            user_relation_item = UserRelationItem()
            fans = [{'id': fan.get('user').get('id'), 'name': fan.get('user').get('screen_name')} for fan in
                    fans]
            user_relation_item['id'] = uid
            user_relation_item['fans'] = fans
            user_relation_item['follows'] = []
            yield user_relation_item
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