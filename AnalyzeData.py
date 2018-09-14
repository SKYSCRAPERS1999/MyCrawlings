# coding: utf-8

# # cpython -u AnalyzeData.py | tee -a output.txt

# # Analyzing
# ## Load weibo_test from csv

import pandas as pd
import pymongo, math, time, re, numpy as np
from snownlp import SnowNLP

week = [ time.strftime('%Y-%m-%d', time.localtime(time.time() - x * 24 * 60 * 60)) for x in range(8) ]
time_re = re.compile('|'.join(week))

# ## load idf

def tf(word, count):
    return count[word] / sum(count.values())

def n_containing(word, count_list):
    return sum(1 for count in count_list if word in count)
    
def idf(word, count_list):
    return math.log(len(count_list) / (1 + n_containing(word, count_list)))

def tfidf(word, count, count_list):
    return tf(word, count) * idf(word, count_list)

# remove not nouns
def tpok(word):
    string = str(word)
    s = SnowNLP(string)
    ls = list(s.tags)
    if len(ls) >= 3:
        return False
    if len(ls) == 1 and 'n' not in ls[0][1]:
        return False
    if len(word) == 2:
        tail = str(word[-1])
        st = SnowNLP(tail)
        ls = list(st.tags)
        if len(ls) == 1 and ls[0][1] == 'v':
            return False
    return True

def get_data_dict(data, stop_words):
    
    print ('In {}, begin, date is {}'.format(get_data_dict.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    data_dict_all = {}
    for dic in data.dict:
        for k, v in eval(dic).items():
            if k in data_dict_all:
                data_dict_all[k] += v
            else:
                data_dict_all[k] = v
                
            if len(k) == 4:
                head, tail = k[2:], k[:-2]
                if head in data_dict_all:
                    data_dict_all[head] += v
                else:
                    data_dict_all[head] = v
                    
                if tail in data_dict_all:
                    data_dict_all[tail] += v
                else:
                    data_dict_all[tail] = v
                    
    data_dict_all = dict([ (k, v) for k, v in data_dict_all.items() if (tpok(k) or v > 50)])
    data_dict_all = dict(sorted(data_dict_all.items(), key=lambda x: math.sqrt(len(x[0]))*x[1], reverse=True))
    data_dict_all = dict([(x,y) for x,y in data_dict_all.items() if (y > 3 and x not in stop_words)]) #remove rare witnesses
    
    print ('In {}, end, date is {}'.format(get_data_dict.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return data_dict_all

def get_clean_word_list(data, data_dict_all):
    
    print ('In {}, begin, date is {}'.format(get_clean_word_list.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    data_words_list_clean = []
    for dic in data.dict:
        data_words_clean = {}
        for k, v in eval(dic).items():
            if k in data_dict_all:
                data_words_clean[k] = v
        data_words_list_clean.append(data_words_clean)

    print ('In {}, end, date is {}'.format(get_clean_word_list.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    return data_words_list_clean

# ### have dict for each, get dict for all
def get_data_idf_dict(data_idf_dict):

    print ('In {}, begin, date is {}'.format(get_data_idf_dict.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    data_idf_dict_all = {}
    for dic in data_idf_dict:
        for k, v in dic.items():
            if k in data_idf_dict_all:
                data_idf_dict_all[k] += v
            else:
                data_idf_dict_all[k] = v
                
            if len(k) == 4:
                head, tail = k[2:], k[:-2]
                if head in data_idf_dict_all:
                    data_idf_dict_all[head] += v
                else:
                    data_idf_dict_all[head] = v
                    
                if tail in data_idf_dict_all:
                    data_idf_dict_all[tail] += v
                else:
                    data_idf_dict_all[tail] = v
    
    data_idf_dict_all = dict(sorted(data_idf_dict_all.items(), key=lambda x: math.sqrt(len(x[0]))*x[1], reverse=True))
    data_idf_dict_all = dict([(x,y) for x,y in data_idf_dict_all.items() if y > 10])
    
    print ('In {}, end, date is {}'.format(get_data_idf_dict.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    return data_idf_dict_all

# ### work idf
# ### 关键词
def output_tf(data_dict_all, collection, day):
    # only tf for all
    print ('In {}, begin, date is {}'.format(output_tf.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    print("Top words in all documents")
    all_scores = { word: tf(word, data_dict_all) for word in data_dict_all}
    all_sorted_words = sorted(all_scores.items(), key=lambda x: math.sqrt(len(x[0]))*x[1], reverse=True)
    
    deletes = collection.find({'created_date': {'$not': time_re}})
    del_id = []
    for dele in deletes:
        if dele.get('_id') != None:
            del_id.append(dele.get('_id'))
    for id in del_id:
        collection.delete_one({'_id': id})
#    collection.delete_many({})
    
    print ('Here1')
    for word, score in all_sorted_words[:500]:
        print("\tWord: {}, TF: {}".format(word, round(score, 5))) 
        collection.insert_one({'word':word, 'tf': round(score, 5), 'created_date': str(day)})
    
    print ('In {}, end, date is {}'.format(output_tf.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
# tf-idf for all
def output_tf_idf(data_dict_all, data_idf_dict_all, collection, day):
    
    print ('In {}, begin, date is {}'.format(output_tf_idf.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    print("Top words in all documents")
    all_scores = { word : tfidf(word, data_dict_all, data_idf_dict_all)
                         for word in data_dict_all }
    all_sorted_words = sorted(all_scores.items(), key=lambda x: math.sqrt(len(x[0]))*x[1], reverse=True)
    
    deletes = collection.find({'created_date': {'$not': time_re}})
    del_id = []
    for dele in deletes:
        if dele.get('_id') != None:
            del_id.append(dele.get('_id'))
    for id in del_id:
        collection.delete_one({'_id': id})
#    collection.delete_many({})
    
    print ('Here2')
    for word, score in all_sorted_words[:500]:
        print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5))) 
        collection.insert_one({'word':word, 'tfidf': round(score, 5), 'created_date': str(day)})
    
    print ('In {}, end, date is {}'.format(output_tf_idf.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
# tf-idf for each
def get_critical_words(data, data_idf_dict):
    
    print ('In {}, begin, date is {}'.format(get_critical_words.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    critical_words = []
    for i, count in enumerate(data.dict):
        #print("Top words in document {}".format(i))
        scores = {word: tfidf(word, count, data_idf_dict) for word in count}
        sorted_words = sorted(scores.items(), key=lambda x: math.sqrt(len(x[0]))*x[1], reverse=True)
        critical_word = []
        for word, score in sorted_words[:20]:
            critical_word.append(word)
            #print("\tWord: {}, TF-IDF: {}".format(word, round(score, 3))) 
        critical_words.append(critical_word)
        if i % 1000 == 0:
            print ('In {}: cnt = {}'.format(get_critical_words.__name__, i))

    print ('In {}, end, date is {}'.format(get_critical_words.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return critical_words
    
def get_word_senti(data):
    
    print ('In {}, begin, date is {}'.format(get_word_senti.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    good_cnt = {}
    bad_cnt = {}
    mid_cnt = {}
    word_senti = {}
    for sen, cri_word in zip(data.senti, data.critical_word):
        #print(sen)
        #print (cri_word)
        for w in cri_word:
            if sen == None or not isinstance(sen, float) or sen < 0:
                continue
            if w not in word_senti:
                word_senti[w] = good_cnt[w] = bad_cnt[w] = mid_cnt[w] = 0
            if (sen > 0.7):
                word_senti[w] += 1
                good_cnt[w] += 1 
            elif (sen < 0.3):
                word_senti[w] -= 1
                bad_cnt[w] += 1 
            else:
                mid_cnt[w] += 1

    print ('In {}, end, date is {}'.format(get_word_senti.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    return {x: (word_senti[x], good_cnt[x], mid_cnt[x], bad_cnt[x]) for x in word_senti}
    
# ### 好坏词语
def output_word_senti(word_senti_posi, word_senti_nega):
    
    print ('In {}, begin, date is {}'.format(output_word_senti.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    for x in word_senti_posi:
        print (x[0], x[1][0], x[1][1], x[1][2], x[1][3])
    for x in word_senti_nega:
        print (x[0], x[1][0], x[1][1], x[1][2], x[1][3])
        
    print ('In {}, end, date is {}'.format(output_word_senti.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
# ### 词语网络
class Graph(object):
    def __init__(self, lb):
        self.node_cnt = 0
        self.id = {}
        self.value = {}
        self.deg = {}
        self.name = {}
        self.edges = {}
        self.lim = lb

def output_graph(data, collection, day, lb=3000):
    #init graph
    
    print ('In {}, begin, date is {}'.format(output_graph.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    wG = Graph(lb)
    for dic in data.dict:
        for x in dic.keys():
            if x not in wG.id:
                wG.id[x] = wG.node_cnt
                wG.node_cnt += 1
                idx = wG.id[x]
                wG.name[idx] = x
                wG.value[idx] = 1
                wG.deg[idx] = 0
                wG.edges[idx] = {}
    
    #remove rare witnesses
    for dic in data.dict:
        for x in dic.keys():
            idx = wG.id[x]
            if idx not in wG.deg:
                wG.deg[idx] = len(dic) - 1
            else:
                wG.deg[idx] += len(dic) - 1
    del_idx = set()
    for idx, val in wG.deg.items():
        if val < wG.lim:
            del_idx.add(idx)
    for idx in del_idx:
        wG.name.pop(idx)
        wG.deg.pop(idx)
        wG.value.pop(idx)
        wG.edges.pop(idx)
    wG.id = dict([ (k, v) for k, v in wG.id.items() if v not in del_idx ])
    
    #add edges
    for dic in data.dict:
        for x in dic.keys():
            if x in wG.id:
                idx = wG.id[x]
                for y in dic.keys():
                    if y != x and y in wG.id:
                        idy = wG.id[y]
                        if idx not in wG.edges[idy]:
                            wG.edges[idx][idy] = 1
                            wG.edges[idy][idx] = 1
                        else:
                            wG.edges[idx][idy] += 1
                            wG.edges[idy][idx] += 1
    
    #sort edges by weight
    wG.edges = dict(sorted([ (k, v) for k, v in wG.edges.items() if len(v) > 1 ], key = lambda x: -len(x[1])))

    #output
    collection.delete_many({})
    for x in [ (wG.name[idx], [ (wG.name[idy], v) for idy, v in chx.items() if idy in wG.name] ) for idx, chx in wG.edges.items()] :
        print (x)
        if len(x) == 2 and len(x[0]) and len(x[1]):
            collection.insert_one({'vertex':x[0], 'adjacent-list': x[1], 'created_date':str(day)})

    print ('In {}, end, date is {}'.format(output_graph.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
# ### Top weibos
def output_hot_text(data, num=150):
    
    print ('In {}, begin, date is {}'.format(output_hot_text.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    num = min(num, len(data) - 1)
    hottest_data = data.sort_values(by='level', axis=0, ascending=False)[:num]
    print (hottest_data.get(['level', 'text']))
    
    print ('In {}, end, date is {}'.format(output_hot_text.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

def read_stop_words():
    
    print ('In {}, begin, date is {}'.format(read_stop_words.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    stop_words = []
    with open('stop_words.txt') as sp:
        for x in sp:
            stop_words.append(x[:-1])

    stop_words = set(stop_words)    
    print ('In {}, end, date is {}'.format(read_stop_words.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return stop_words

def run():
    #dependence: ../ScrapyDatas/weibo_test_data.csv, ../ScrapyDatas/weibo_idf_dict.csv
    #dependence: SnowNLP
    print ('In {}, begin, date is {}'.format(run.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 2000)
    pd.set_option('display.max_colwidth',1000)    
    
    stop_words = read_stop_words()
    data = pd.read_csv('../ScrapyDatas/weibo_test_data.csv')
    
    data_dict_all = get_data_dict(data, stop_words)
    data.dict = get_clean_word_list(data, data_dict_all)
    
    #data_idf_dict = pd.read_csv('../ScrapyDatas/weibo_idf_dict.csv', header=None)
    #data_idf_dict = [ eval(dic) for dic in np.array(data_idf_dict[1]).tolist() ]

    data_idf_dict = []
    data_idf_iterator = pd.read_csv('../ScrapyDatas/weibo_idf_dict.csv', chunksize=10000, header=None)
    for data_chunk in data_idf_iterator:
        data_idf_dict_chunk = [ eval(dic) for dic in np.array(data_chunk[1]).tolist() ]
        data_idf_dict.extend(data_idf_dict_chunk)
        
    data_idf_dict_all = get_data_idf_dict(data_idf_dict)
    
    ##open Mongodb
    mongo_uri = 'mongodb://impulse:njuacmicpc@120.79.139.239/weibo'
    client = pymongo.MongoClient(host=mongo_uri, port=27017)
    db = client['weibo']
    collection_tf = db['word_tf']
    collection_tfidf = db['word_tfidf']
    collection_good = db['good_words']
    collection_bad = db['bad_words']
    collection_graph = db['word_graph']

    day = time.strftime('%Y-%m-%d', time.localtime(time.time())) 
    
    critical_words_list = get_critical_words(data, data_idf_dict)
    data['critical_word'] = critical_words_list
    data.to_csv('../ScrapyDatas/weibo_test_data.csv')
    
    ## Output tf and tf-idfs and write into Mongodb
    print ('In {}: Analyzing tf and writing Mongodb now'.format(run.__name__))
    output_tf(data_dict_all, collection_tf, day)
    print ('In {}: Analyzing tfidf and writing Mongodb now'.format(run.__name__))
    output_tf_idf(data_dict_all, data_idf_dict_all, collection_tfidf, day)
#    
    ## Output texts with most emotions and write into Mongodb
    print ('In {}: Analyzing word senti now'.format(run.__name__))
    word_senti = get_word_senti(data)
    word_senti_posi = sorted(word_senti.items(), key=lambda x: x[1][0], reverse=True)[:500]
    word_senti_nega = sorted(word_senti.items(), key=lambda x: x[1][0], reverse=False)[:500]
    output_word_senti(word_senti_posi, word_senti_nega)
    
    print ('In {}: Writing good word senti into mongodb'.format(run.__name__))

#    collection_good.delete_many({})
    deletes = collection_good.find({'created_date': {'$not': time_re}})
    del_id = []
    for dele in deletes:
        if dele.get('_id') != None:
            del_id.append(dele.get('_id'))
    for id in del_id:
        collection_good.delete_one({'_id': id})
    
    for (word, (sen, good, mid, bad)) in word_senti_posi:
        collection_good.insert_one({'word':str(word), 'senti':float(sen), 'good':int(good), 'mid':int(mid)
            , 'bad': int(bad), 'created_date':str(day)})
    print ('In {}: Writing bad word senti into mongodb'.format(run.__name__))
#    collection_bad.delete_many({})
    
    deletes = collection_bad.find({'created_date': {'$not': time_re}})
    del_id = []
    for dele in deletes:
        if dele.get('_id') != None:
            del_id.append(dele.get('_id'))
    for id in del_id:
        collection_bad.delete_one({'_id': id})
        
    for (word, (sen, good, mid, bad)) in word_senti_nega:
        collection_bad.insert_one({'word':str(word), 'senti':float(sen), 'good':int(good), 'mid':int(mid)
            , 'bad': int(bad), 'created_date':str(day)})
    
    ## Output relation graphs and write into Mongodb
    print ('In {}: Analyzing graph and writing into mongodb'.format(run.__name__))
    output_graph(data, collection_graph, day)
    
    ## Output hottest texts
    output_hot_text(data)
    
    client.close()    
    
    print ('In {}, end, date is {}'.format(run.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

if __name__ == '__main__':
    run()
