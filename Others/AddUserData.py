# coding: utf-8
# ## Load weibo_test from database into csv

import pymongo, time, re
import pandas as pd

mongo_uri = 'mongodb://impulse:njuacmicpc@120.79.139.239/weibo'
days = [ time.strftime('%Y-%m-%d', time.localtime(time.time() - x * 24 * 60 * 60)) for x in range(2) ]

def add_user_data():
    
    print ('In {}, begin, date is {}'.format(add_user_data.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    client = pymongo.MongoClient(host=mongo_uri, port=27017)
    db = client['weibo']
    collection = db['weibos']
    collection_user = db['users']
    
    for day in days:
        results = collection.find({'created_date':day}, {'_id':1,'user':1}, no_cursor_timeout = True)
        print ('In {}: len of db: {}'.format(add_user_data.__name__, results.count()))
        
        for (i, result) in enumerate(results):
            user_id, _id = result.get('user'), result.get('_id')
            if user_id != None and _id != None:
                try:
                    user_results = collection_user.find({'id':int(user_id)}, {'name':1,'avatar':1})
                    for user_result in user_results:
                        name = user_result.get('name')
                        avatar = user_result.get('avatar')
                        if i % 100 == 0:
                            print ('weibo {}: {}'.format(i, name))
                        if name != None and avatar != None:
                            collection.update({'_id': _id}, {'$set': {'name': name, 'avatar': avatar} }, False)
                except Exception as err:
                    print("Error {}".format(err))
                
    client.close()
    print ('In {}, end, date is {}'.format(add_user_data.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

def add_clean_text():
    
    print ('In {}, begin, date is {}'.format(add_clean_text.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    client = pymongo.MongoClient(host=mongo_uri, port=27017)
    db = client['weibo']
    collection = db['weibos']
    
    for day in days:
        results = collection.find({'created_date':day}, {'_id':1,'text':1,'full_text':1}, no_cursor_timeout = True)
        print ('In {}: len of db: {}'.format(add_user_data.__name__, results.count()))
        
        for (i, result) in enumerate(results):
            cur_text, _id = result.get('full_text'), result.get('_id')
            if cur_text == None:
                cur_text = result.get('text')
            if  _id != None:
                try:
                    if cur_text != None:
                        cur_text = re.sub('<.*?>', ' ', cur_text)
                    if cur_text != None:
                        cur_text = re.sub(' +', ' ', cur_text)
                    collection.update({'_id': _id}, {'$set': {'clean_text': cur_text} }, False)
                    if i % 100 == 0:
                        print (i, cur_text[:20])
                    
                except Exception as err:
                    print("Error {}".format(err))
    
    client.close()
    print ('In {}, end, date is {}'.format(add_clean_text.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    return
    
def run():
    
    #dependence: jieba_dict_companys, stop_words.txt, stop_letters.txt
    print ('In {}, begin, date is {}'.format(run.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    add_user_data()
    add_clean_text()
    
    print ('In {}, end, date is {}'.format(run.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

if __name__ == '__main__':
    run()
