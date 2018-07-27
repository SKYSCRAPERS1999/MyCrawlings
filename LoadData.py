
# coding: utf-8
# ## Load weibo_test from database into csv

import pymongo, re, jieba, requests, time, json
import jieba.posseg as postag
import pandas as pd

def get_data():
    client = pymongo.MongoClient(host='120.79.139.239', port=27017)
    db = client['weibo']
    collection = db['weibos']
    results = collection.find({}, {'user':1,'attitudes_count':1,'comments_count':1,'reposts_count':1,'text':1,'full_text':1})
    data = pd.DataFrame(list(results))[:500] # for test
    if 'attitudes_count' in data.columns: ## if it is normal
        data = data.get(['user','attitudes_count','comments_count','reposts_count','text', 'full_text'])
        data.columns = ['user', 'at_cnt', 'cmt_cnt', 'rep_cnt', 'text', 'f_text']
        for i in range(len(data)):
            if len(str(data.loc[i, 'f_text'])) > 135:
                data.loc[i, 'text'] = data.loc[i, 'f_text']
        data = data.drop('f_text', axis=1)        
        print ('In {}: data loaded, len {}'.format(get_data.__name__, len(data)))
    else:
        print ('In {}: some errors occur'.format(get_data.__name__))        
    return data

def read_stop_words(): 
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
    return (stop_words, re_stop_letter)

def get_clean_text(data, output=True):
    texts = []
    for cnt, raw in enumerate(data.text):
        del_name = re.findall('@([^ |<|:|\(|\)|\\|\/|<|>|\[|\]]+)', raw)
        for name in del_name:
            raw = re.sub(name, '', raw)
        raw = re.sub('<br />', '，', raw)
        raw = re.sub('[^\u4e00-\u9fa5|，|!|。]+|\?{1}|:{1}', '', raw)
        texts.append(raw)
        
        if cnt % 100 == 0 and output == True:
            print ('In {}: cnt = {}'.format(get_clean_text.__name__, cnt))
            
    if len(texts) == len(data):
        return pd.Series(texts)
    else:
        print ('In {}: not the same length'.format(get_clean_text.__name__))
        return None

def get_words(data, re_stop_letter, stop_words, output=True):
    words = []
    for cnt, raw in enumerate(data.c_text):
        result = postag.cut(raw)
        raw = [x.word for x in result if (len(x.word) > 1 and 'n' in x.flag and re.search(re_stop_letter, x.word) == None and x.word not in stop_words)]
        words.append(raw)
        
        if cnt % 100 == 0 and output == True:
            print ('In {}: cnt = {}'.format(get_words.__name__, cnt))
            
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
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'access_token': '24.cb5b8cccad6a49c21d4cccd1a047f9ae.2592000.1534940191.282335-11569351'
    }
    positive_prob = []
    for cnt, text in enumerate(data.c_text):
        start_time = time.clock()
        post_json = {
            "text": text
        }

        response = requests.post('https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify',
                                params=params, headers=headers, json=post_json)
        if response.status_code != 200:
            time.sleep(2.0)
            response = requests.post('https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify',
                                params=params, headers=headers, json=post_json)

        if response.text != None:
            res_json = json.loads(response.text)
            if res_json.get('items') != None and res_json.get('items')[0].get('positive_prob') != None: 
                prob = res_json.get('items')[0].get('positive_prob')
                #print (prob)
                positive_prob.append(prob)
            else:
                print('-1')
                positive_prob.append('-1')
        else:
            print('-1')
            positive_prob.append('-1')
        elapsed = (time.clock() - start_time)
        time.sleep(0.25 - elapsed)

        if cnt % 100 == 0 and output:
            print ('In {}: cnt = {}'.format(get_sentiment.__name__, cnt))
    if len(data) != len(positive_prob):
        print ('In {}: length not equal'.format(get_sentiment.__name__))
        
    return pd.Series(positive_prob)

def run():
    
    #dependence: jieba_dict_companys, stop_words.txt, stop_letters.txt
    jieba.load_userdict('jieba_dict_companys')
    stop_words, re_stop_letter = read_stop_words()

    data = get_data()
    data['c_text'] = get_clean_text(data)
    data['words'] = get_words(data=data, re_stop_letter=re_stop_letter, stop_words=stop_words)
    # notice ! in use !
    # data['senti'] = get_sentiment(data)
    word_counts = [ get_word_count(lst) for lst in data.words]
    data['dict'] = pd.Series(word_counts)  
    data['level'] = (1 + data.at_cnt) * (1 + data.rep_cnt) * (1 + data.cmt_cnt)
    data2 = pd.read_csv('../ScrapyDatas/weibo_test_data.csv')
    data['senti'] = data2.senti

    data.to_csv('../ScrapyDatas/weibo_test_data2.csv')
    print ('In {}: data written'.format(run.__name__))

if __name__ == '__main__':
    run()