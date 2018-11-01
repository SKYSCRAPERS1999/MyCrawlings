#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 13:20:40 2018

@author: impulse
"""
import time, pymongo

from_uri = 'mongodb://impulse:njuacmicpc@120.79.139.239/weibo'
to_uri = 'mongodb://106.12.42.98/weibo'

week = [ time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60 * i)) for i in range(7) ]

def run():
    from_client = pymongo.MongoClient(host=from_uri, port=27017)
    from_db = from_client['weibo']
    
    to_client = pymongo.MongoClient(host=to_uri, port=27017)
    to_db = to_client['weibo']
    
    ## update all
    cols = ['weibos', 'good_words', 'bad_words', 'word_tf', 'word_tfidf', 'word_graph']
    for col in cols:
        print ('Begin inserting items in collection {}'.format(col))
        from_collection = from_db[col]
        to_collection = to_db[col]
        
        for day in week:
            from_result = from_collection.find({'created_date':day})
            cur_count = from_result.count()
            to_result = to_collection.find({'created_date':day})
            prev_count = to_result.count()
            print ('(Collection, day) = ({}, {}): {} items, {} items previously had'.format(col, day, cur_count, prev_count))
            if prev_count < 0.99 * cur_count:
                for i, item in enumerate(from_result):
                    try:
                        if col == 'weibos':
                            to_collection.update({'id':item['id']}, 
                                                  item, upsert=True, multi=False)
                        elif col == 'word_graph':
                            to_collection.update({'vertex':item['vertex']}, 
                                                  item, upsert=True, multi=False)
                        else:
                            to_collection.update({'created_date':item['created_date'],
                            'word':item['word']}, item, upsert=True, multi=False)
                        if i % 100 == 0:
                            print('cnt = {}'.format(i)) 
                    except Exception as err:
                        print('Error {}'.format(err))
                        
        print ('Finish inserting items in collection {}'.format(col))
        
    from_client.close()
    to_client.close()
    
if __name__ == '__main__':
    run()