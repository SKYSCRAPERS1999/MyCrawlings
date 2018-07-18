# -*- coding: utf-8 -*-
from scrapy import Request, Spider
import json, re
from weibo.items import UserItem, UserRelationItem, WeiboItem, GarbageItem
from weibo.spiders.user_start import st_users
from weibo.spiders.garbages import garbages
import random

class WeibocnSpider(Spider):
    name = 'weibocn'
    allowed_domains = ['weibo.cn']
    start_urls = ['http://weibo.cn/']
    
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    #start_users = ['1896820725', '1216826604', '1613005690', '2014433131', '1645823934', '1653661844', '1364334665', '2144596567']
    #start_users = ['1896820725','1613005690','1216826604','1808523312','1497042545','1243477063','5828706619','3911653032','1651428902','2868676035','1865425867','2000961721','1274553861','1959993400','5578381471','1659801380','1288764341','2014878391','1692895670','1747752685','2418201593','5393848625','5228879991','5839701517','3781574891','1096941450','2478892631','6241116541','5617133616','1907214345','5902314049','6076409077','1355610915','2627698865','5178785227','5091912327','1227655400','1563749484','1401495827','1639325085','1036117702','1987877075','2637129912','2385224017','1699910791','6177581254','2191812860','1735053670','2191848774','1893601564','3138051401','2475263107','2372849541','5099703397','2092759380','5637985133','1974447435','5745213591','1679149403','1764187882','5198672477','3981807543','2039949672','1847428005','1642574504','1726276573','1991713215','1788641607','1832487154','1154814883','1901501937','1610132560','1214074324','1988070841','1680664482','1846128547','1789302347','1764828222','1784666497','5130283857','1916701507','1916959611','3469463810','1501664143']
    #start_users = ['1896820725','1613005690','1216826604','1497042545','1808523312','1243477063','5828706619','3911653032','1651428902','2868676035','1865425867','2000961721','1274553861','1959993400','5578381471','1659801380','1288764341','2014878391','2082892671','1692895670','3781574891','1972519063','6040549176','2446599755','2698139935','2687110553','1496961083','5726382604','1690898540','1596329427','5170186722','1938424152','1680664482','2183570524','5891711854','1665056143','3866971988','1727386613','1740627424','1283357352','1663612603','2211400920','3694257343','1807916530','1069205631','1832598427','2248818320','1217680514','2072724293','1667983181','1746692527','3243067320','1241952424','1224180577','1659486012','5839701517','1846227957','1832487154','1649259794','1932326853','5617133616','5242156161','1698631892','2098879567','5690705426','1296904573','5707030090','6410905934','1909253791','1962788401','2369862891','2988751824','2612383011','1789372347','1816256200','1401495827','2475263107','2029444043','1824681831','1496941737','3425332364','2823363883','1214074324','1284760130','1270787132','1403025472','2150749951','2363823727','1528250204','1769379434','2205307052','2219266972','5737116459','1882147360','2679053417','1352799650','6294136160','1878611631','6219614281','2792204924','1791653972','1504965870','1661526105','1068385283','2617289195','1905617941','3486065922','5384479977','5693268749','1426568373','2155299332','3766896324','1657987915','2006664175','3026723501','5688800032','1302489457','1733811557','2975116822','1055769173','5052471499','1455543965','3214687194','1745211532','214771687','2361595240','1319475951','1750087417','1753021103','1403473045','1052636041','3190081773','1437964265','1731528401','1076301085','5627481668','2436093373','1192187564','2810402890','5662156039','2125720981','2013613854','5726497135','5105624987','2131473734','5606951581','5517181603','2640810863','1654492464','1262666992','1691025530','3698934484','2298768207','1604852752','1003716184','1927885484','2198602110','2239286777','1950001183','1096941450','6241116541','2770610290','1926909715','1641561812','1649173367','1881799654','2360878652','5957534844','1496810113','3079645245','1801487174','1718493627','1988800805','1405463773','1058334880','2853016445','2450957454','5126392303','1333620355','1682231463','1863057363','5344772541','1609962335','2006106727','1942859227','5955111244','5277513683','1529124462','1775728572','5635020865','1769784332','1725765581','1322308864','5547578924','5078179296','1918424072','2128731935','2031760143','1723144472','2112915613','5236434677','2368532821','5819781579','5992632476','1987616333','2040371363','2214689312','2413906205','1845445230','2284695883','3947185985','5198672477','5104289648','2454655415','5573459134','2610157832','2051128701','3315535714','1357171084','2986339052','5724162547','5802046608','5499527890','5607764110','5623827459','5489831354','5587554443','2728637310','1255868135','1781268537','2020940691','5731053881','5713877791','5807411813','1744890360','5848021716','5869552120','5688313870','1065321695','2945371067','3850424312','5141753661','6021575012','3740652193','2028006072','3110050494','5254803086','1562593561','3162242715','6014913564','1056490737','5496662318','1309619851','5515166761','2423863464','2954189190','5647517211','1784650280','3936639322','2615345454','5926603736','2809343792','5076920737','3096052471','3173956325','1446362094','2115414832','1899720387','1290699133','1328150093','2913029503','1318246293','1218431470','3298909953','1775952217','2150574053','6450244479','6192576729','3241532904','6391771955','6326625389','1891131232','1216903164','2307961073','6007277756','1554616541','1501664143','2028249037','5760620653','1774853192','1875300075','3604316867','2108959974','1988070841','2076656187','2748268615','2065452327','2291170527','1579652672','2506194002','1766377343','1891389147','1219938242','2862475010','1668665607','3304479404','2428826174','1458594614','1672627214','1856020347','2420497571','2736670755','1652537294','1732668371','1841830123','1704145940','2105408284','2544903971','1449369585','2286071245','1902377862','2206389075','3486017690','2450724134','5496486161','5374203256','1730828001','3441455610','5976681897','1773286334','5671933168','1615302742','2287873742','2304063124','5501705786','5794806495','1402901591','2474959734','1897447655','3858780599','5580987800','5517706848','2845776900','3760046807','2343095160','1302154547','1709416584','1134437870','1902075497']
    start_users = st_users
    start_garbages = garbages
    
    regex = re.compile('(?:谈股|说股|讲股|论股|看股|港股|美股|理财师|A股|经济政策|短线|炒股|荐股|盈亏|炒股|股利|股海|股民|股票|个股|做空|诱多|诱空|踏空|长空|短空|长多|短多|死多|翻多|翻空|多杀多|扎空|空仓|建仓|满仓|斩仓|减仓|加仓|重仓|清仓|套牢|补仓|仓位|庄家|震仓|追涨|杀跌|止盈|抄底|逃顶|盘整|回档|坐庄|吸筹|对敲|洗盘|散户|中户|坐轿|抬轿|筹码|抢帽子|多头陷阱|空头陷阱|护盘|跳空|开盘价|收盘价|最高价|最低价|成交量|放量|缩量|热门股|冷门股|白马股|黑马股|龙头股|阴跌|换手率|现手|平开|低开|高开|内盘|外盘|均价|浮筹|市盈率|含权|回购|基本面分析|量比|每股|收益|市净率|探底|填权|停牌|退市)')    
    nregex = re.compile('(?:公司|企业|CEO|基金会|大学|学院|政府)')
    
    output_info = True
    finish_ID = set(st_users)  # 记录已爬的微博ID
    garbage_ID = set(garbages)
    garbage_buffer = set()
    
    def start_requests(self):
        random.shuffle(self.start_users)
        for uid in self.start_users:
            yield Request(self.user_url.format(uid=uid), callback=self.parse_user)
            
    def validify_user(self, user_info):
        if user_info.get('id') == None:
            return False
        uid = user_info.get('id')   
        if user_info.get('description') == None or user_info.get('verified_reason') == None or user_info.get('verified_type') == None:
            self.garbage_buffer.add(str(uid))
            return False
        if user_info.get('verified_type') == -1:
            self.garbage_buffer.add(str(uid))
            return False
        if re.search(self.regex, user_info.get('description')) == None or re.search(self.nregex, user_info.get('description')) != None:
            self.garbage_buffer.add(str(uid))
            return False
        return True
        
    def parse_user(self, response):
        """
        解析用户信息
        :param response: Response对象
        """
        if len(self.garbage_buffer) >= 50:
            garbage_item = GarbageItem()
            garbage_item['gid'] = self.garbage_buffer
            for gid in self.garbage_buffer:
                self.garbage_ID.add(gid)
            self.garbage_buffer.clear()
            yield garbage_item
        
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            uid = user_info.get('id')
            if (str(uid) in self.finish_ID) or (str(uid) not in self.garbage_ID):
                return
            
            if not self.validify_user(user_info):
                return
                                
            self.logger.info(response)
            
            user_item = UserItem()
            
            field_map = {
                'id': 'id', 'name': 'screen_name', 'avatar': 'profile_image_url', 'cover': 'cover_image_phone',
                'gender': 'gender', 'description': 'description', 'fans_count': 'followers_count',
                'follows_count': 'follow_count', 'weibos_count': 'statuses_count', 'verified': 'verified',
                'verified_reason': 'verified_reason', 'verified_type': 'verified_type'
            }
            
            for field, attr in field_map.items():
                user_item[field] = user_info.get(attr)
                
            self.finish_ID.add(str(uid))    
            self.output_info = True
            
            yield user_item               
            
            if (len(self.finish_ID) % 5 == 0 or len(self.garbage_ID) % 5 == 0) and self.output_info == True:
                self.output_info = False
                self.logger.info('finish: {}'.format(len(self.finish_ID)))
                self.logger.info('garbage: {}'.format(len(self.garbage_ID)))
                if len(self.finish_ID) % 100 == 0:
                    tmp = []
                    for x in self.finish_ID:
                        tmp.append(x)
                    self.logger.info(tmp)
                    
            # 微博
            #yield Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
            #              meta={'page': 1, 'uid': uid})
            
            # 关注
            if user_info.get('followers_count') != None and user_info.get('follow_count') != None and user_info.get('followers_count') > 3 * user_info.get('follow_count'):
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
                    if (uid not in self.finish_ID) and (uid not in self.garbage_ID):
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