# coding: utf-8
# ## Load weibo_test from database into csv

import pymongo, time
import pandas as pd

mongo_uri = 'mongodb://impulse:njuacmicpc@120.79.139.239/weibo'

def add_user_data():
    
    print ('In {}, begin, date is {}'.format(add_user_data.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    client = pymongo.MongoClient(host=mongo_uri, port=27017)
    db = client['weibo']
    collection = db['weibos']
    collection_user = db['users']
    results = collection.find({}, {'_id':1,'user':1})
    print ('In {}: len of db: {}'.format(add_user_data.__name__, results.count()))
    
    for (i, result) in enumerate(results):
        user_id, _id = result.get('user'), result.get('_id')
        if user_id != None and _id != None:
            try:
                user_results = collection_user.find({'id':int(user_id)}, {'name':1,'avatar':1})
                for user_result in user_results:
                    name = user_result.get('name')
                    avatar = user_result.get('avatar')
                    print ('weibo {}: {}'.format(i, name))
                    if name != None and avatar != None:
                        collection.update({'_id': _id}, {'$set': {'name': name, 'avatar': avatar} }, False)
            except Exception as err:
                print("Error {}".format(err))
    client.close()
    print ('In {}, end, date is {}'.format(add_user_data.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

def run():
    
    #dependence: jieba_dict_companys, stop_words.txt, stop_letters.txt
    print ('In {}, begin, date is {}'.format(run.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    add_user_data()
    
    print ('In {}, end, date is {}'.format(run.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

if __name__ == '__main__':
    run()
