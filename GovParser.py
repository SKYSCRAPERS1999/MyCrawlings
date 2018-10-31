# coding: utf-8
import requests, re, time, pymysql, jieba
import jieba.posseg as postag
#tables = [ 'wms']
tables = [ 'wms', 'swb','nyj', 'zscqj', 'jbw', 'zjh', 'yjh', 'rmyh']
lim = 10

def get_sql(table = 'jbw', dec = 0):
    month = time.strftime('%Y-%m', time.localtime(time.time() - 24 * 3600 * 30 * dec))
    sql = "SELECT title FROM gov.{} WHERE date > '{}-01' and date <= '{}-31'".format(table, month, month)
    return sql

def get_sentense_dict():
    print ('In {}, begin, date is {}'.format(get_sentense_dict.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    db = pymysql.connect(host='119.29.190.115', user='guest', password='njuacmicpc',
                         port=3306, db='gov', write_timeout = 6, read_timeout = 6)
    cursor = db.cursor()
    dic_by_num = {}
    for dec in range(lim):
        dic_by_num[dec] = []
        for table in tables:
            sql = get_sql(table, dec)
            try:
                cursor.execute(sql)
                db.commit()
                for row in cursor.fetchall():
                    if len(row) > 0:
#                         print (row[0])
                        dic_by_num[dec].append(row[0])
            except Exception as err:
                print("Error {}".format(err))
                time.sleep(5)
    db.close()
    print ('In {}, end, date is {}'.format(get_sentense_dict.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dic_by_num

def aggregate_tables():
    print ('In {}, begin, date is {}'.format(aggregate_tables.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    db = pymysql.connect(host='119.29.190.115', user='guest', password='njuacmicpc',
                         port=3306, db='gov', write_timeout = 6, read_timeout = 6)
    cursor = db.cursor()
    
    input_list = []
    for table in tables:
        sql = 'SELECT * FROM gov.{}'.format(table)
        try:
            cursor.execute(sql)
            db.commit()
            for row in cursor.fetchall():
                if len(row) > 0:
                    while len(row) < 4:
                        row.append('')
                    input_list.append({'pos': row[0], 'title': row[1], 'link': row[2], 'date': row[3], 'origin': table})
        except Exception as err:
            print("Error {}".format(err))
            time.sleep(5)
    db.close()
    print ('In {}, end, date is {}'.format(aggregate_tables.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return input_list

def insert_summary_table(input_list):
    print ('In {}, begin, date is {}'.format(insert_summary_table.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    db = pymysql.connect(host='119.29.190.115', user='impulse', password='njuacmicpc',
                         port=3306, db='gov', write_timeout = 6, read_timeout = 6)
    cursor = db.cursor()
    try:
        for dic in input_list:
#             print (dic)
            sql_insert(db=db,cursor=cursor,data=dic,table='summary')
    except Exception as err:
        print("Error {}".format(err))
        time.sleep(5)
    db.close()
    print ('In {}, end, date is {}'.format(insert_summary_table.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    return

def get_words(sentence_list):
    words = []
    jieba.enable_parallel(8)
    for raw in sentence_list:
        result = postag.cut(raw)
        raw = [x.word for x in result if (len(x.word) > 1 and 'n' in x.flag)]
        words += raw           
    return words

def get_word_count(lst, stop_words = None, re_stop_letter = None):
    count = {}
    for x in lst:
        if ((stop_words == None or x not in stop_words) and 
           (re_stop_letter == None or re.search(re_stop_letter, x) == None)):
            if x in count:
                count[x] += 1
            else:
                count[x] = 1
    return count

def sql_insert(db, cursor, table, data):
    keys = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    sql = 'insert into {table}({keys}) values ({values}) on duplicate key update'.format(table=table, 
            keys=keys, values=values)
    update = ','.join([" {key} = %s".format(key=key) for key in data])
    sql += update
    try:
        if cursor.execute(sql, tuple(data.values())*2):
            print('Successful')
            db.commit()
        else:
            print ('Nothing to do')
    except:
        print ('Failed')
        db.rollback()

def insert_wordcnt(sentense_dict):
    print ('In {}, begin, date is {}'.format(insert_wordcnt.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    db = pymysql.connect(host='119.29.190.115', user='impulse', password='njuacmicpc',
                         port=3306, db='gov', write_timeout = 6, read_timeout = 6)
    cursor = db.cursor()
    for dec in range(lim):
        month = time.strftime('%Y-%m', time.localtime(time.time() - 24 * 3600 * 30 * dec))
        word_counts = get_word_count(get_words(sentense_dict[dec]))
        word_dict_list = [ {'word':x[0], 'month': month, 'tf': int(x[1])} for x in word_counts.items()]
        try:
            for dic in word_dict_list:
#                 print (dic)
                sql_insert(db=db,cursor=cursor,data=dic,table='word_tf')
        except Exception as err:
            print("Error {}".format(err))
            time.sleep(5)
    print ('In {}, end, date is {}'.format(insert_wordcnt.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    db.close()

def dic_with_name(dic, name):
    dic['type'] = name
    return dic

def insert_other_table(input_list, regex_dict):
    print ('In {}, begin, date is {}'.format(insert_other_table.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    db = pymysql.connect(host='119.29.190.115', user='impulse', password='njuacmicpc',
                         port=3306, db='gov', write_timeout = 6, read_timeout = 6)
    cursor = db.cursor()
    table_list = ['TZGG','HYPX','ZCFB','ZCJD','ZFSJ','YWDD']
    
    input_list_with_type = []
    
    for dic in input_list:
        tit = dic['title']
        try:
            is_inserted = False
            for name in table_list[:-1]:
                if tit != None and re.search(regex_dict[name], tit) != None:
                    sql_insert(db=db,cursor=cursor,data=dic,table=name)
                    input_list_with_type.append(dic_with_name(dic, name))
#                     print (dic_with_name(dic,name))
                    is_inserted = True
                    
            if is_inserted == False or re.search(regex_dict[table_list[-1]], tit) != None:
                sql_insert(db=db,cursor=cursor,data=dic,table=table_list[-1])
                if is_inserted == False: input_list_with_type.append(dic_with_name(dic,table_list[-1]))
#                 print (dic_with_name(dic,table_list[-1]))
                
        except Exception as err:
            print("Error {}".format(err))
            time.sleep(5)
            
    db.close()
    print ('In {}, end, date is {}'.format(insert_other_table.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return input_list_with_type

def run():
    #通知公告(TZGG)：'通知|公告|号令|函|通报|公示|问卷'
    #会议培训(HYPX)：'培训|开班|学习|会议|会$|召开|的办法|的决定'
    #政策发布(ZCFB)：'发布|印发|决定|意见
    #政策解读(ZCJD)：'解读|谈|答'
    #政府数据(ZFSJ)：'年.*表$|报$|报告|月报|季报|年报$
    #要闻导读(YWDD)：'活动|开展' (以及前面未出现的所有)
    regex = dict()
    regex['TZGG'] = re.compile('通知|公告|号令|函|通报|公示|问卷')
    regex['HYPX'] = re.compile('培训|开班|学习|会议|会$|召开|的办法|的决定')
    regex['ZCFB'] = re.compile('发布|印发|决定|意见')
    regex['ZCJD'] = re.compile('解读|谈|答')
    regex['ZFSJ'] = re.compile('年.*表$|报$|报告|月报|季报|年报')
    regex['YWDD'] = re.compile('活动|开展')
    
    input_list = aggregate_tables()
    
    input_list_with_type = insert_other_table(input_list, regex)
    
    insert_summary_table(input_list_with_type)

    sdict = get_sentense_dict()

    insert_wordcnt(sdict)

if __name__ == '__main__':
    run()

