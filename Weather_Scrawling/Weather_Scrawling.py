import pymysql, requests, re, time, json
import numpy as np, pandas as pd

## Mysql Template

import pymysql
db = pymysql.connect(host='119.29.190.115', user='root', password='njuacmicpc',
                         port=3306, db='weather', write_timeout = 10, read_timeout = 6)
cursor = db.cursor()

def sql_insert(db, cursor, table, data):
    keys = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    sql = 'insert into {table}({keys}) values ({values}) on duplicate key update'.format(table=table, 
            keys=keys, values=values)
    update = ','.join([" {key} = %s".format(key=key) for key in data])
    sql += update
    #print (sql)
    try:
        if cursor.execute(sql, tuple(data.values())*2):
            print('Successful')
            db.commit()
        else:
            print ('Nothing to do')
    except:
        print ('Failed on {}'.format(data))
        db.rollback()

def get_list(data, i = 0, K = 3):
    n = len(data)
    return ','.join([str(x) for x in data[i * n // K: (i + 1) * n // K]])

url = 'http://api.data.cma.cn:8090/api'
form = {
    'userId': '542355761660o8fuw',
    'pwd': 'bJ4ImKk',
    'dataFormat': 'json',
    'interfaceId': 'getSurfEleByTimeRangeAndStaID',
    'dataCode': 'SURF_CHN_MUL_HOR',
    'timeRange': '[{}0000,{}0000]'.format(time.strftime('%Y%m%d23', time.localtime(time.time() - 6 * 24 * 60 * 60)),
                 time.strftime('%Y%m%d23', time.localtime(time.time() - 1 * 24 * 60 * 60))),
    'staIDs': '',
    'elements': 'TEM,Station_Id_C,Year,Mon,Day,Hour',
}

K = 3
def read_id_list():
    id_list = []
    with open("./id_list", "r") as fp:
        for x in fp:
            id_list.append(str(x[:-1]))
    return id_list

def run():
    id_list = read_id_list()
    print (id_list)
    station_df = pd.read_excel('./China_SURF_Station.xlsx')
    station_dict = {}
    for id, name, prov in zip(station_df.区站号, station_df.站名, station_df.省份):
        station_dict[str(id)] = (name, prov)
    
    texts = []
    for i in range(K):
        form['staIDs'] = get_list(id_list, i)
        response = requests.get(url = url, params = form)
        texts.append(response.text)
        
    result = [json.loads(x) for x in texts]
    print (result)
    for i in range(K):
        result[i] = result[i]['DS']
    
    for i in range(K):
        for j in range(len(result[i])):
            name, prov = station_dict[result[i][j]['Station_Id_C']]
            result[i][j]['name'] = name
            result[i][j]['prov'] = prov
        result[i] = [ x for x in result[i] if x['Hour'] in ['2','8','14','20']]
        results = []
    for i in range(K):
        results += result[i]
    
    from collections import defaultdict
    dic_by_id = defaultdict(lambda: list())
    for x in results:
        dic_by_id[x['Station_Id_C']].append(x)
    
    dic_by_name_agg = {}
    for id in id_list:
        name = station_dict[id][0]
        cur = dic_by_id[id]
        aggregate_weather = []
        n = len(cur)
        i = 0; j = 0;
        while (cur[i]['Hour'] != '2'): i += 1
        while (i + 3 < n):
            avg = 0.25 * (float(cur[i]['TEM']) + float(cur[i+1]['TEM']) + float(cur[i+2]['TEM']) + float(cur[i+3]['TEM']))
            if(cur[i]['Day']!=cur[i+3]['Day']):
                
                print ('i, n = {}, {}'.format(i, n))
                print(name, id)
                print(cur[i]['Day'],cur[i+1]['Day'],cur[i+2]['Day'],cur[i+3]['Day'])
                print(cur[i]['Hour'],cur[i+1]['Hour'],cur[i+2]['Hour'],cur[i+3]['Hour'])
#                while (cur[i]['Day']==cur[i+1]['Day']): i += 1
                i += 1
                
                continue
            else:
                date = '{x[0]}-{x[1]:0>2}-{x[2]:0>2}'.format(x = (cur[i]['Year'],cur[i]['Mon'],cur[i]['Day']) )
                aggregate_weather.append({'prov':cur[i]['prov'],'year':cur[i]['Year'],'month':cur[i]['Mon'],
                                      'day':cur[i]['Day'],'TEM_Avg':avg,'date':date})
            i += 4
            
        dic_by_name_agg[name] = aggregate_weather
    
    for key, dic_list in dic_by_name_agg.items():
        for dic in dic_list:
            cur = {}
            cur['name'] = key
            cur.update(dic)
            print (cur)
            sql_insert(db, cursor, 'TEM', cur)
    db.close()
    
if __name__ == '__main__':
    run()

