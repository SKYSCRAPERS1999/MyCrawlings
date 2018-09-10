# coding: utf-8
# ## Load weibo_test from database into csv

import pymongo, re, jieba, requests, time, json, math
import jieba.posseg as postag
import pandas as pd

mongo_uri = 'mongodb://impulse:njuacmicpc@120.79.139.239/weibo'

def get_data():
    
    print ('In {}, begin, date is {}'.format(get_data.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    client = pymongo.MongoClient(host=mongo_uri, port=27017)
    db = client['weibo']
    collection = db['weibos']
    results = collection.find({}, {'id':1,'user':1,'attitudes_count':1,'comments_count':1,'reposts_count':1,'text':1,'full_text':1})
    print ('In {}: len of db: {}'.format(get_data.__name__, results.count()))
    data = pd.DataFrame(list(results)) # for test
    if 'attitudes_count' in data.columns: ## if it is normal
        data = data.get(['id', 'user','attitudes_count','comments_count','reposts_count','text', 'full_text'])
        data.columns = ['id', 'user', 'at_cnt', 'cmt_cnt', 'rep_cnt', 'text', 'f_text']
        for i in range(len(data)):
            if len(str(data.loc[i, 'f_text'])) > 135:
                data.loc[i, 'text'] = data.loc[i, 'f_text']
        data = data.drop('f_text', axis=1)        
        print ('In {}: data loaded, len {}'.format(get_data.__name__, len(data)))
    else:
        print ('In {}: some errors occur'.format(get_data.__name__))        
    
    client.close()
    print ('In {}, end, date is {}'.format(get_data.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    return data

def prettify_text(data, output=True):
    
    print ('In {}, begin, date is {}'.format(prettify_text.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    texts = []
    for cnt, text in enumerate(data.text):
        text = re.sub('<.*?>', '', text)
        text = text.replace("\\n", '')
        texts.append(text)
        if cnt % 1000 == 0 and output == True:
            print ('In {}: cnt = {}'.format(prettify_text.__name__, cnt))

    print ('In {}, end, date is {}'.format(prettify_text.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
           
    if len(texts) == len(data):
        return pd.Series(texts)
    else:
        print ('In {}: not the same length'.format(prettify_text.__name__))
        return None

def read_stop_words():
    
    print ('In {}, begin, date is {}'.format(read_stop_words.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    stop_words = []
    stop_letters = []
    with open('stop_words.txt') as sp:
        for x in sp:
            stop_words.append(x[:-1])
    with open('stop_letters.txt') as sp:
        for x in sp:
            stop_letters.append(x[:-1])
    stop_words = set(stop_words)
    re_stop_letter = re.compile('|'.join(stop_letters))
    
    print ('In {}, end, date is {}'.format(read_stop_words.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return (stop_words, re_stop_letter)

def get_clean_text(data, output=True):
    
    print ('In {}, begin, date is {}'.format(get_clean_text.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    texts = []
    for cnt, raw in enumerate(data.text):
        try:
            del_name = re.findall('@([^ |<|:|\(|\)|\\|\/|<|>|\[|\]]+)', raw)
            for name in del_name:
                raw = re.sub(name, '', raw)
        except Exception as err:
            print("Error {}".format(err))
            pass
        
        raw = re.sub('<br />', '，', raw)
        raw = re.sub('[^\u4e00-\u9fa5|，|!|。]+|\?{1}|:{1}', '', raw)
        texts.append(raw)
        
        if cnt % 1000 == 0 and output == True:
            print ('In {}: cnt = {}'.format(get_clean_text.__name__, cnt))
    
    print ('In {}, end, date is {}'.format(get_clean_text.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
        
    if len(texts) == len(data):
        return pd.Series(texts)
    else:
        print ('In {}: not the same length'.format(get_clean_text.__name__))
        return None

def get_words(data, re_stop_letter, stop_words, output=True):
    
    print ('In {}, begin, date is {}'.format(get_words.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    words = []
    for cnt, raw in enumerate(data.c_text):
        result = postag.cut(raw)
        raw = [x.word for x in result if (len(x.word) > 1 and 'n' in x.flag and re.search(re_stop_letter, x.word) == None and (x.word not in stop_words))]
        words.append(raw)
        
        if cnt % 1000 == 0 and output == True:
            print ('In {}: cnt = {}'.format(get_words.__name__, cnt))
    
    print ('In {}, end, date is {}'.format(get_words.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
            
    return pd.Series(words)

def get_word_count(lst):
    count = {}
    for x in lst:
        if x in count:
            count[x] += 1
        else:
            count[x] = 1
    return count

# # sentiments
def get_sentiment(data, output=True):
    
    print ('In {}, begin, date is {}'.format(get_sentiment.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    headers = {'Content-Type': 'application/json'}
    params = {'access_token': '24.9ac5bfe09d008481c4dc699f69288ed1.2592000.1537058351.282335-11569351'}
    positive_prob = []
    omit_cnt = 0
    for cnt, (text, senti) in enumerate(zip(data.c_text, data.senti)):
        if is_float(senti) and float(senti) > 0.0 and float(senti) < 1.0:
            omit_cnt += 1
            positive_prob.append(float(senti))
            if omit_cnt % 100 == 0:
                print ('In {}: omit: {}'.format(get_sentiment.__name__, omit_cnt))                
            continue
            print ("place 1")
        else:
            if text == None or len(text) <= 2:
                positive_prob.append(float(-1))
                continue
                
            start_time = time.clock()
            post_json = {
                "text": str(text)[:256]
            }
            
            try:
                response = requests.post('https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify',
                                        params=params, headers=headers, json=post_json, timeout=1.0)
                if response.status_code != 200:
                    time.sleep(2.0)
                    print ('status_code = {}'.format(response.status_code))
                    response = requests.post('https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify',
                                        params=params, headers=headers, json=post_json, timeout=1.0)
                print ("place 2")
                if response.text != None:
                    res_json = json.loads(response.text)
                    if res_json.get('items') != None and res_json.get('items')[0].get('positive_prob') != None: 
                        prob = res_json.get('items')[0].get('positive_prob')
                        #print (prob)
                        positive_prob.append(prob)
                    else:
                        print('In {}: {}'.format(get_sentiment.__name__, float(-1)))
                        positive_prob.append(float(-1))
                    print ("place 3")
                else:
                    print('In {}: {}'.format(get_sentiment.__name__, float(-1)))
                    positive_prob.append(float(-1))
                    print ("place 4")
                
            except Exception as err:
                positive_prob.append(float(-1))
                print("Error {}".format(err))
                time.sleep(2)
            
            elapsed = (time.clock() - start_time)
            if 0.04 > elapsed:
                time.sleep(0.04 - elapsed)
                    
#        if cnt % 1000 == 0 and output:
        if cnt % 1000 == 0 and output or True:
            print ('In {}: cnt = {}'.format(get_sentiment.__name__, cnt))
            
    if len(data) != len(positive_prob):
        print ('In {}: length not equal'.format(get_sentiment.__name__))
        
    print ('In {}, end, date is {}'.format(get_sentiment.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return pd.Series(positive_prob)

is_float = lambda x: x.replace('.','',1).isdigit() and "." in x

def run():
    
    #dependence: jieba_dict_companys, stop_words.txt, stop_letters.txt
    print ('In {}, begin, date is {}'.format(run.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    jieba.load_userdict('jieba_dict_companys')
    stop_words, re_stop_letter = read_stop_words()
    
    data = get_data()
    data['text'] = prettify_text(data)
    data['c_text'] = get_clean_text(data)
    data['words'] = get_words(data=data, re_stop_letter=re_stop_letter, stop_words=stop_words)
    
    client = pymongo.MongoClient(host=mongo_uri, port=27017)
    db = client['weibo']
    collection = db['weibos']
        
    word_counts = [ get_word_count(lst) for lst in data.words]
    data['dict'] = pd.Series(word_counts)  
    data['level'] = (1 + data.at_cnt) * (1 + data.rep_cnt) * (1 + data.cmt_cnt)
    
    data_prev = pd.read_csv('../ScrapyDatas/weibo_test_data.csv')
    senti_dict = dict([ (str(id), str(sen)) for id, sen in zip(data_prev.id, data_prev.senti)])
    
    data['senti'] = pd.Series([])
    
    new_senti = []
    for id, sen in zip(data.id, data.senti):
        if str(id) in senti_dict:
            new_senti.append(senti_dict[str(id)])
        else:
            new_senti.append('')
    
    if len(new_senti) != len(data):
        print('In {}: senti length error'.format(run.__name__))
        return    
    
    data['senti'] = pd.Series(new_senti)
    data['senti'] = get_sentiment(data)
    
    print ('In {}: Writing data now'.format(run.__name__))
    
    data.to_csv('../ScrapyDatas/weibo_test_data.csv')
    print ('In {}: data written'.format(run.__name__))
    
    print ('In {}: Writing Mongodb now'.format(run.__name__))
    
    print ('In {}: Writing Mongodb Words now'.format(run.__name__))
    for x in zip(list(data.id), list(data.words)):
        collection.update({'id':str(x[0])}, {'$set': {'words':list(set(x[1]))} })
        
    print ('In {}: Writing Mongodb Senti now'.format(run.__name__))
    for x in zip(list(data.id), list(data.senti)):
        collection.update({'id':str(x[0])}, {'$set': {'senti':float(x[1])} })
    print ('In {}: Writing Mongodb Level now'.format(run.__name__))
    for x in zip(list(data.id), list(data.level)):
        collection.update({'id':str(x[0])}, {'$set': {'level':int(x[1])} })
    client.close()
    print ('In {}: Mongodb written'.format(run.__name__))

    print ('In {}, end, date is {}'.format(run.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

if __name__ == '__main__':
    run()
