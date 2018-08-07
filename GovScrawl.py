## Mysql Template

## Test Mysql

import pymysql
from lxml import etree
import requests, re, time
from bs4 import BeautifulSoup
headers = {
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
}

def create_db(cursor, name):
    sql = 'create database {name} default character set utf8'.format(name=name)
    cursor.execute(sql)

def create_table(cursor, name):
    sql = 'create table if not exists {} (pos VARCHAR(32), title VARCHAR(512), link VARCHAR(512), date VARCHAR(64), PRIMARY KEY (link))'.format(name)
    cursor.execute(sql)

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
        print ('Failed')
        db.rollback()

# Goverment Datas

## ShangWuBu

### China

def get_swb_china():
    print ('In {}, begin, date is {}'.format(get_swb_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
        
    base_url = 'http://www.mofcom.gov.cn'
    response = requests.get(base_url + '/article/zhengcejd/', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//*[@id="wrap"]/div[2]/div/div[1]/div[2]/ul/li/a[1]/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '//*[@id="wrap"]/div[2]/div/div[1]/div[2]/ul/li/a[1]/@href'
    links = html.xpath(xpath)
    # print (links)
    xpath = '//*[@id="wrap"]/div[2]/div/div[1]/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)
    # print (dates)
    data_china = [ (t, l, d, 'china') for (t, l, d) in zip(titles, links, dates) ]

    response = requests.get(base_url + '/article/b/', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//*[@id="wrap"]/div[2]/div/div[1]/div[2]/ul/li/a/text()'
    titles = html.xpath(xpath)
    xpath = '//*[@id="wrap"]/div[2]/div/div[1]/div[2]/ul/li/a/@href'
    links = html.xpath(xpath)
    links = [ base_url + str(x) for x in links]
    xpath = '//*[@id="wrap"]/div[2]/div/div[1]/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)

    data_china = data_china + [ (t, l, d, 'china') for t, l, d in zip(titles, links, dates) ]

    dict_china = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_china]
  
    print (len(dict_china))

    print ('In {}, end, date is {}'.format(get_swb_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_china

### JiangSu

def get_swb_jiangsu():
    
    print ('In {}, begin, date is {}'.format(get_swb_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://swt.jiangsu.gov.cn'
    response = requests.get(base_url + '/col/col12660/index.html', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    # print (text)
    regex = re.compile('<a href="(.*)" target="_blank">(.*)</a><span style=".*"> \((.*)\)</span>')

    data_jiangsu = [(x[1], base_url+x[0], x[2].replace('/', '-'), 'jiangsu') for x in re.findall(pattern=regex, string=text)]
    
    dict_jiangsu = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_jiangsu]
    
    print (len(dict_jiangsu))
    
    print ('In {}, end, date is {}'.format(get_swb_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_jiangsu

## ZheJiang

def get_swb_zhejiang():
    
    print ('In {}, begin, date is {}'.format(get_swb_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://zhejiang.mofcom.gov.cn'
    response = requests.get(base_url + '/article/sjtongzhigg', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//*[@id="main"]/div[2]/div/ul/li/a/text()'
    titles = html.xpath(xpath)
    xpath = '//*[@id="main"]/div[2]/div/ul/li/a/@href'
    links = html.xpath(xpath)
    links = [ base_url + str(x) for x in links]
    xpath = '//*[@id="main"]/div[2]/div/ul/li/span/text()'
    dates = html.xpath(xpath)
    dates = [x.split()[0] for x in dates]

    data_zhejiang = [ (t, l, d, 'zhejiang') for t, l, d in zip(titles, links, dates) ]
    
    dict_zhejiang = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_zhejiang]
    
    print (len(dict_zhejiang))

    print ('In {}, end, date is {}'.format(get_swb_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_zhejiang

## GuangDong

def get_swb_guangdong():
    
    print ('In {}, begin, date is {}'.format(get_swb_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.gdcom.gov.cn/zwgk/zcwj/'
    response = requests.get(base_url, headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None

    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '/html/body/div[2]/div/div[2]/ul/li/a/text()'
    titles = html.xpath(xpath)
    xpath = '/html/body/div[2]/div/div[2]/ul/li/a/@href'
    links = html.xpath(xpath)
    tlinks = []
    for x in links:
        x = str(x)
        if x != None and x[:2] == './':
            x = base_url + x[2:]
        tlinks.append(x)
    links = tlinks
    
    xpath = '/html/body/div[2]/div/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)
    dates = [x.replace(' ', '') for x in dates]
    
    data_guangdong = [ (t, l, d, 'guangdong') for t, l, d in zip(titles, links, dates) ]
        
    dict_guangdong = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_guangdong]
    
    print (len(dict_guangdong))

    print ('In {}, end, date is {}'.format(get_swb_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_guangdong


## ShangWuBuWaiMaoSi

def get_wms_china():
    
    print ('In {}, begin, date is {}'.format(get_wms_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://wms.mofcom.gov.cn'
    response = requests.get(base_url + '/article/zcfb/ax/', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//*[@id="leftList"]/div[2]/ul/li/a[1]/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '//*[@id="leftList"]/div[2]/ul/li/a[1]/@href'
    links = html.xpath(xpath)
    links = [ base_url + str(x) for x in links]
    # print (links)
    xpath = '//*[@id="leftList"]/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)
    dates = [x.split()[0] for x in dates]
    # print (dates)

    data_china = [ (t, l, d, 'china') for (t, l, d) in zip(titles, links, dates) ]

    response = requests.get(base_url + '/article/zcfb/g/', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//*[@id="leftList"]/div[2]/ul/li/a[1]/text()'
    titles = html.xpath(xpath)
    xpath = '//*[@id="leftList"]/div[2]/ul/li/a[1]/@href'
    links = html.xpath(xpath)
    links = [ base_url + str(x) for x in links]
    xpath = '//*[@id="leftList"]/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)
    dates = [x.split()[0] for x in dates]
    
    data_china = data_china + [ (t, l, d, 'china') for t, l, d in zip(titles, links, dates) ]

    dict_china = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_china]
  
    print (len(dict_china))

    print ('In {}, end, date is {}'.format(get_wms_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_china

def get_wms_jiangsu():

    print ('In {}, begin, date is {}'.format(get_wms_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://swt.jiangsu.gov.cn'
    
    response = requests.get(base_url + '/col/col57691/index.html', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    regex = re.compile('<a href="(.*)" target="_blank" .*title="(.*)">.*</a><span.*> \((.*)\)</span>')
    data_jiangsu = [(x[1], base_url+x[0], x[2].replace('/', '-'), 'jiangsu') for x in re.findall(pattern=regex, string=text)]
    
    response = requests.get(base_url + '/col/col57692/index.html', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    regex = re.compile('<a href="(.*)" target="_blank" .*title="(.*)">.*</a><span.*> \((.*)\)</span>')
    data_jiangsu += [(x[1], base_url+x[0], x[2].replace('/', '-'), 'jiangsu') for x in re.findall(pattern=regex, string=text)]
    
    dict_jiangsu = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_jiangsu]
    
    print (len(dict_jiangsu))

    print ('In {}, end, date is {}'.format(get_wms_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_jiangsu

def get_wms_zhejiang():

    print ('In {}, begin, date is {}'.format(get_wms_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.zcom.gov.cn'
    
    response = requests.get(base_url + '/col/col1385815/index.html', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')

    html = etree.HTML(text)
    xpath = '//*[@id="con_two_2"]/div[position()>1]/a[1]/text()'
    titles = html.xpath(xpath)  
    xpath = '//*[@id="con_two_2"]/div[position()>1]/a[1]/@href'
    links = html.xpath(xpath)
    links = [ base_url + str(x) for x in links]
    
    xpath = '//*[@id="con_two_2"]/div[position()>1]/a[1]/span/text()'
    dates = html.xpath(xpath)
    data_zhejiang = [ (t, l, d, 'zhejiang') for t, l, d in zip(titles, links, dates) ]

    ################
    
    xpath = '//*[@id="con_three_1"]/div[position()>1]/a[1]/text()'
    titles = html.xpath(xpath)  
    xpath = '//*[@id="con_three_1"]/div[position()>1]/a[1]/@href'
    links = html.xpath(xpath)
    links = [ base_url + str(x) for x in links]
    
    xpath = '//*[@id="con_three_1"]/div[position()>1]/a[1]/span/text()'
    dates = html.xpath(xpath)
    data_zhejiang += [ (t, l, d, 'zhejiang') for t, l, d in zip(titles, links, dates) ]
    
    dict_zhejiang = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_zhejiang]
  
    print (len(dict_zhejiang))

    print ('In {}, end, date is {}'.format(get_wms_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_zhejiang

def get_wms_guangdong():
    
    print ('In {}, begin, date is {}'.format(get_wms_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://go.gdcom.gov.cn'
    
    response = requests.get(base_url + '/article.php?typeid=9', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')

    html = etree.HTML(text)
    xpath = '/html/body/div[3]/div/div[2]/div/div[2]/div[2]/ul/li/h6/a[1]/text()'
    titles = html.xpath(xpath)  
    xpath = '/html/body/div[3]/div/div[2]/div/div[2]/div[2]/ul/li/h6/a[1]/@href'
    links = html.xpath(xpath)
    links = [ base_url + '/' + str(x) for x in links]
    
    xpath = '/html/body/div[3]/div/div[2]/div/div[2]/div[2]/ul/li/h6/small/text()'
    dates = html.xpath(xpath)
    data_guangdong = [ (t, l, d, 'guangdong') for t, l, d in zip(titles, links, dates) ]

    dict_guangdong = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_guangdong]
  
    print (len(dict_guangdong))

    print ('In {}, end, date is {}'.format(get_wms_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_guangdong



## ZhiShiChanQuanJu

def get_zscqj_china():
    
    print ('In {}, begin, date is {}'.format(get_zscqj_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.sipo.gov.cn'
    
    response = requests.get(base_url + '/gwywj/index.htm', headers=headers, timeout=10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/a[1]/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/a[1]/@href'
    links = html.xpath(xpath)
    # print (links)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)
    # print (dates)
    data_china = [ (t, l, d, 'china') for (t, l, d) in zip(titles, links, dates) ]

    response = requests.get(base_url + '/dtxx/index.htm', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/a[1]/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/a[1]/@href'
    links = html.xpath(xpath)
    ## !!!!!
    links = [ base_url + '/dtxx/' + str(x) for x in links] 
    # print (links)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)
    # print (dates) 
    data_china = data_china + [ (t, l, d, 'china') for t, l, d in zip(titles, links, dates) ]

    response = requests.get(base_url + '/zfgg/index.htm', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/a[1]/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/a[1]/@href'
    links = html.xpath(xpath)
    ## !!!!!
    links = [ base_url + '/zfgg/' + str(x) for x in links]
    # print (links)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)
    # print (dates) 
    data_china = data_china + [ (t, l, d, 'china') for t, l, d in zip(titles, links, dates) ]
    
    response = requests.get(base_url + '/gztz/index.htm', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/a[1]/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/a[1]/@href'
    links = html.xpath(xpath)
    ## !!!!!
    links = [ base_url + '/gztz/' + str(x) for x in links]
    # print (links)
    xpath = '/html/body/div/div/div/div[4]/div/div[2]/ul/li/span/text()'
    dates = html.xpath(xpath)
    # print (dates) 
    data_china = data_china + [ (t, l, d, 'china') for t, l, d in zip(titles, links, dates) ]
    
    
    dict_china = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_china]
  
    print (len(dict_china))

    print ('In {}, end, date is {}'.format(get_zscqj_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_china

def get_zscqj_jiangsu():

    print ('In {}, begin, date is {}'.format(get_zscqj_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://jsip.jiangsu.gov.cn'
    
    response = requests.get(base_url + '/col/col3300/index.html', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    regex = re.compile('<a href="(.*)" TARGET="_blank" >.*<div class="text">(.*)</div>.*<div class="text-date">(.*)</div>.*</a>')
    data_jiangsu = [(x[1], base_url+x[0], x[2], 'jiangsu') for x in re.findall(pattern=regex, string=text)]
    
    response = requests.get(base_url + '/col/col3252/index.html', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    regex = re.compile('<a href="(.*)" TARGET="_blank" >.*<div class="text">(.*)</div>.*<div class="text-date">(.*)</div>.*</a>')
    data_jiangsu += [(x[1], base_url+x[0], x[2], 'jiangsu') for x in re.findall(pattern=regex, string=text)]
    
    dict_jiangsu = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_jiangsu]
    
    print (len(dict_jiangsu))

    print ('In {}, end, date is {}'.format(get_zscqj_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_jiangsu

def get_zscqj_zhejiang():

    print ('In {}, begin, date is {}'.format(get_zscqj_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.zjpat.gov.cn'
    
    response = requests.get(base_url + '/interIndex.do?method=list22&dir=/zjszscqj/tzgg', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8').replace('\r\n', '')
    text = re.sub(' +', ' ', text)

    regex = re.compile('<a href="([^>]*?)" title="([^>]*?)" target="_blank" class="color_01">.*?</a> </td> <td.[^>]*?> \((.*?)\) </td> </tr>')
    data_zhejiang = [(x[1], base_url+'/'+x[0], x[2], 'zhejiang') for x in re.findall(pattern=regex, string=text)]
    
    response = requests.get(base_url + '/interIndex.do?method=list2&dir=/zjszscqj/xwdt/sxdt', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8').replace('\r\n', '')
    text = re.sub(' +', ' ', text)
    regex = re.compile('<a href="([^>]*?)" title="([^>]*?)" target="_blank" class="color_01">.*?</a> </td> <td.[^>]*?> \((.*?)\) </td> </tr>')
    data_zhejiang += [(x[1], base_url+'/'+x[0], x[2], 'zhejiang') for x in re.findall(pattern=regex, string=text)]
    
    dict_zhejiang = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_zhejiang]
    
    print (len(dict_zhejiang))
    
    print ('In {}, end, date is {}'.format(get_zscqj_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_zhejiang


def get_zscqj_guangdong():

    print ('In {}, begin, date is {}'.format(get_zscqj_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.gdipo.gov.cn'
    
    response = requests.get(base_url + '/gdipo/gdipodt/list.shtml', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8').replace('\r\n', '')
    text = re.sub(' +', ' ', text)
    regex = re.compile('<li> <a href="(.*?)" target="_blank" >(.*?)</a> <div class="time_div"> <span class="time">(.*?)</span> </div> </li>')
    data_guangdong = [(x[1], base_url+x[0], x[2], 'guangdong') for x in re.findall(pattern=regex, string=text)]

    response = requests.get(base_url + '/gdipo/tzgg/list.shtml', headers=headers, timeout=10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8').replace('\r\n', '')
    text = re.sub(' +', ' ', text)
    regex = re.compile('<li> <a href="(.*?)" target="_blank" >(.*?)</a> <div class="time_div"> <span class="time">(.*?)</span> </div> </li>')
    data_guangdong += [(x[1], base_url+x[0], x[2], 'guangdong') for x in re.findall(pattern=regex, string=text)]
   
    dict_guangdong = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_guangdong]
    
    print (len(dict_guangdong))
    
    print ('In {}, end, date is {}'.format(get_zscqj_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_guangdong

### Very/interIndex.do?method=list2&dir=/zjszscqj/xwdt/sxdt Important to match \r\n...
### re.findall(pattern='<table>([\s\S]*?)<\/table>', string=text)


## NengYuanJu

def get_nyj_china():
    print ('In {}, begin, date is {}'.format(get_nyj_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.nea.gov.cn'
    
    response = requests.get(base_url + '/xwzx/nyyw.htm', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//div[@class="content"]/div/ul/li/a/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '//div[@class="content"]/div/ul/li/a/@href'
    links = html.xpath(xpath)
    # print (links)
    xpath = '//div[@class="content"]/div/ul/li/span/text()'
    dates = html.xpath(xpath)
    # print (dates)
    data_china = [ (t, l, d, 'china') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_china = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_china]
  
    print (len(dict_china))
    
    print ('In {}, end, date is {}'.format(get_nyj_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_china

def get_nyj_jiangsu():
    print ('In {}, begin, date is {}'.format(get_nyj_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://jsb.nea.gov.cn'
    
    response = requests.get(base_url + '/info/community/101.html', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'gbk').replace('\r\n', '')
    text = re.sub(' +', ' ', text)
    html = etree.HTML(text)

    regex = re.compile('<a href="([^>]*?)" target=_blank>(.*?)</a></td><td.*?> <p.*?>\[(.*?)\] </td>')
    data_jiangsu = [(x[1], base_url+x[0], x[2], 'jiangsu') for x in re.findall(pattern=regex, string=text)]
    
    dict_jiangsu = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2].replace('/', '-')} for x in data_jiangsu]
    
    print (len(dict_jiangsu))
    
    print ('In {}, end, date is {}'.format(get_nyj_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_jiangsu

def get_nyj_zhejiang():
    print ('In {}, begin, date is {}'.format(get_nyj_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://zjb.nea.gov.cn'

    response = requests.get(base_url + '/article/zygg/d1/', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'gbk')
    html = etree.HTML(text)
    xpath = '//div[@class="d5"]/a/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '//div[@class="d5"]/a/@href'
    links = html.xpath(xpath)
    links = [base_url + x for x in links]
    # print (links)
    xpath = '//div[@class="d5"]/span/text()'
    dates = html.xpath(xpath)
    # print (dates)
    data_zhejiang = [ (t, l, d, 'zhejiang') for (t, l, d) in zip(titles, links, dates) ]
    
    response = requests.get(base_url + '/article/ywdd/', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'gbk')
    html = etree.HTML(text)
    xpath = '//div[@class="d5"]/a/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '//div[@class="d5"]/a/@href'
    links = html.xpath(xpath)
    links = [base_url + x for x in links]
    # print (links)
    xpath = '//div[@class="d5"]/span/text()'
    dates = html.xpath(xpath)
    # print (dates)
    data_zhejiang += [ (t, l, d, 'zhejiang') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_zhejiang = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_zhejiang]
  
    print (len(dict_zhejiang))
    
    print ('In {}, end, date is {}'.format(get_nyj_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_zhejiang

def get_nyj_guangdong():
    ## Infact, it is nyj of southern china
    print ('In {}, begin, date is {}'.format(get_nyj_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://nfj.nea.gov.cn'
    
    response = requests.get(base_url + '/frontIndex/showNews.do?type=3', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//div[@class="new_list2"]/ul/li/a/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '//div[@class="new_list2"]/ul/li/a/@href'
    links = html.xpath(xpath)
    # print (links)
    xpath = '//div[@class="new_list2"]/ul/li/span/text()'
    dates = html.xpath(xpath)
    # print (dates)
    data_guangdong = [ (t, l, d, 'guangdong') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_guangdong = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_guangdong]
    
    print (len(dict_guangdong))

    print ('In {}, end, date is {}'.format(get_nyj_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_guangdong


## JinBiaoWei

def get_jbw_china():
    print ('In {}, begin, date is {}'.format(get_jbw_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.cfstc.org' 
    
    response = requests.get(base_url + '/jinbiaowei/2929484/index.html', headers=headers, timeout = 10)
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//table[@opentype="page"]/tbody/tr/td/ul/li/a[1]/text()'
    titles = html.xpath(xpath)
    # print (titles)
    xpath = '//table[@opentype="page"]/tbody/tr/td/ul/li/a[1]/@href'
    links = html.xpath(xpath)
    ## !!!!!
    links = [ base_url + '/gztz/' + str(x) for x in links]
    # print (links)
    xpath = '//table[@opentype="page"]/tbody/tr/td/ul/li/span/text()'
    dates = html.xpath(xpath)
    # print (dates) 
    data_china = [ (t, l, d, 'china') for t, l, d in zip(titles, links, dates) ]
    
    dict_china = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_china]
  
    print (len(dict_china))

    print ('In {}, end, date is {}'.format(get_jbw_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_china

## ZhengJianHui

def get_zjh_china():
    print ('In {}, begin, date is {}'.format(get_zjh_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    base_url = 'http://www.csrc.gov.cn/pub/zjhpublic' 
    
    driver.get(base_url + '/index.htm?channel=3300/3311/')
    driver.switch_to.frame("DataList")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
#     html = driver.page_source
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="mc"]/div/a')
    urls = [ele.get_attribute("href") for ele in elements if len(ele.text) > 0]
    titles = [ele.text for ele in elements if len(ele.text) > 0]
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="fbrq"]')
    dates = [ele.text for ele in elements if len(ele.text) > 0]
    dates = [ date.replace('年','-').replace('月','-').replace('日','') for date in dates]

    data_china = [(x[0], x[1], x[2]) for x in zip(titles,urls,dates)]    
    
    driver.get(base_url + '/index.htm?channel=3300/3302/')
    driver.switch_to.frame("DataList")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
#     html = driver.page_source
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="mc"]/div/a')
    urls = [ele.get_attribute("href") for ele in elements if len(ele.text) > 0]
    titles = [ele.text for ele in elements if len(ele.text) > 0]
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="fbrq"]')
    dates = [ele.text for ele in elements if len(ele.text) > 0]
    dates = [ date.replace('年','-').replace('月','-').replace('日','') for date in dates]

    data_china += [(x[0], x[1], x[2]) for x in zip(titles,urls,dates)]

    
    driver.quit()    
    
    dict_china = [{'pos': 'china', 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_china]
    
    print (len(dict_china))
    
    print ('In {}, end, date is {}'.format(get_zjh_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_china

def get_zjh_jiangsu():
    print ('In {}, begin, date is {}'.format(get_zjh_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    base_url = 'http://www.csrc.gov.cn/pub/zjhpublicofjs' 
    
    driver.get(base_url + '/index.htm?channel=3284/3565/')
    driver.switch_to.frame("DataList")
    
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
#     html = driver.page_source
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="mc"]/div/a')
    urls = [ele.get_attribute("href") for ele in elements if len(ele.text) > 0 ]
    titles = [ele.text for ele in elements if len(ele.text) > 0 ]
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="fbrq"]')
    dates = [ele.text for ele in elements if len(ele.text) > 0 ]
    dates = [ date.replace('年','-').replace('月','-').replace('日','') for date in dates]

    data_jiangsu = [(x[0], x[1], x[2]) for x in zip(titles,urls,dates)]    
    
    driver.quit()    
    
    dict_jiangsu = [{'pos': 'jiangsu', 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_jiangsu]
    
    print (len(dict_jiangsu))
    
    print ('In {}, end, date is {}'.format(get_zjh_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_jiangsu

def get_zjh_zhejiang():
    print ('In {}, begin, date is {}'.format(get_zjh_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    base_url = 'http://www.csrc.gov.cn/pub/zjhpublicofzj' 
    
    driver.get(base_url + '/index.htm?channel=3284/3565/')
    driver.switch_to.frame("DataList")
    
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
#     html = driver.page_source
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="mc"]/div/a')
    urls = [ele.get_attribute("href") for ele in elements if len(ele.text) > 0 ]
    titles = [ele.text for ele in elements if len(ele.text) > 0 ]
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="fbrq"]')
    dates = [ele.text for ele in elements if len(ele.text) > 0 ]
    dates = [ date.replace('年','-').replace('月','-').replace('日','') for date in dates]

    data_zhejiang = [(x[0], x[1], x[2]) for x in zip(titles,urls,dates)]    
    
    driver.quit()    
    
    dict_zhejiang = [{'pos': 'zhejiang', 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_zhejiang]
    
    print (len(dict_zhejiang))
    
    print ('In {}, end, date is {}'.format(get_zjh_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_zhejiang

def get_zjh_guangdong():
    print ('In {}, begin, date is {}'.format(get_zjh_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    base_url = 'http://www.csrc.gov.cn/pub/zjhpublicofgd' 
    
    driver.get(base_url + '/index.htm?channel=3284/3565/')
    driver.switch_to.frame("DataList")
    
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
#     html = driver.page_source
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="mc"]/div/a')
    urls = [ele.get_attribute("href") for ele in elements if len(ele.text) > 0 ]
    titles = [ele.text for ele in elements if len(ele.text) > 0 ]
    elements = driver.find_elements_by_xpath('//div[@class="row"]/li[@class="fbrq"]')
    dates = [ele.text for ele in elements if len(ele.text) > 0 ]
    dates = [ date.replace('年','-').replace('月','-').replace('日','') for date in dates]

    data_guangdong = [(x[0], x[1], x[2]) for x in zip(titles,urls,dates)]    
    
    driver.quit()    
    
    dict_guangdong = [{'pos': 'guangdong', 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_guangdong]
    
    print (len(dict_guangdong))
    
    print ('In {}, end, date is {}'.format(get_zjh_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_guangdong


## YinJianHui

def get_yjh_china():
    
    print ('In {}, begin, date is {}'.format(get_yjh_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.cbrc.gov.cn'
    
    response = requests.get(base_url + '/chinese/home/docViewPage/114.html', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//div[@class="right"]//tr/td[1]/a/text()'
    titles = html.xpath(xpath)
#     print (titles)
    xpath = '//div[@class="right"]//tr/td[1]/a/@href'
    links = html.xpath(xpath)
    links = [base_url + link for link in links]
    # print (links)
    xpath = '//div[@class="right"]//tr/td[2]/text()'
    dates = html.xpath(xpath)
    dates = [date.replace('\r\n\t', '').replace('\t','') for date in dates]
    # print (dates)
    data_china = [ (t, l, d, 'china') for (t, l, d) in zip(titles, links, dates) ]
    
    
    dict_china = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_china]
  
    print (len(dict_china))

    print ('In {}, end, date is {}'.format(get_yjh_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_china

def get_yjh_zhejiang():
    
    print ('In {}, begin, date is {}'.format(get_yjh_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.cbrc.gov.cn'
    
    response = requests.get(base_url + '/zhejiang/pcjgDocMore/600610/left.html', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//div[@class="bookw3"]/a/@title'
    titles = html.xpath(xpath)
#     print (titles)
    xpath = '//div[@class="bookw3"]/a/@href'
    links = html.xpath(xpath)
    links = [base_url + link for link in links]
    # print (links)
    xpath = '//div[contains(@class,"work_list_date")]/text()'
    dates = html.xpath(xpath)
    dates = [date.replace('\r\n\t', '') for date in dates]
    # print (dates)
    data_zhejiang = [ (t, l, d, 'zhejiang') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_zhejiang = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_zhejiang]
  
    print (len(dict_zhejiang))

    print ('In {}, end, date is {}'.format(get_yjh_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_zhejiang

def get_yjh_guangdong():
    
    print ('In {}, begin, date is {}'.format(get_yjh_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.cbrc.gov.cn'
    
    response = requests.get(base_url + '/guangdong/pcjgDocMore/601710/left.html', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//div[@class="bookw3"]/a/@title'
    titles = html.xpath(xpath)
#     print (titles)
    xpath = '//div[@class="bookw3"]/a/@href'
    links = html.xpath(xpath)
    links = [base_url + link for link in links]
    # print (links)
    xpath = '//div[contains(@class,"work_list_date")]/text()'
    dates = html.xpath(xpath)
    dates = [date.replace('\r\n\t', '') for date in dates]
    # print (dates)
    data_guangdong = [ (t, l, d, 'guangdong') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_guangdong = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_guangdong]
  
    print (len(dict_guangdong))

    print ('In {}, end, date is {}'.format(get_yjh_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_guangdong

def get_yjh_jiangsu():
    
    print ('In {}, begin, date is {}'.format(get_yjh_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    base_url = 'http://www.cbrc.gov.cn'
    
    response = requests.get(base_url + '/jiangsu/pcjgDocMore/600810/left.html', headers=headers, timeout = 10)   
    if (response.status_code != 200):
        return None
    text = str(response.content, 'utf-8')
    html = etree.HTML(text)
    xpath = '//div[@class="bookw3"]/a/@title'
    titles = html.xpath(xpath)
#     print (titles)
    xpath = '//div[@class="bookw3"]/a/@href'
    links = html.xpath(xpath)
    links = [base_url + link for link in links]
    # print (links)
    xpath = '//div[contains(@class,"work_list_date")]/text()'
    dates = html.xpath(xpath)
    dates = [date.replace('\r\n\t', '') for date in dates]
    # print (dates)
    data_jiangsu = [ (t, l, d, 'jiangsu') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_jiangsu = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_jiangsu]
  
    print (len(dict_jiangsu))

    print ('In {}, end, date is {}'.format(get_yjh_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_jiangsu


## RenMinYinHang

def get_rmyh_china():
    print ('In {}, begin, date is {}'.format(get_rmyh_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    base_url = 'http://www.pbc.gov.cn'
    
    driver.get(base_url + '/diaochatongjisi/116219/index.html')
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    
    xpath = '//td[@height=23 or contains(@class, "font14")]/a[@href and @target="_blank"]'
    elements = driver.find_elements_by_xpath(xpath)
    links = [ele.get_attribute("href") for ele in elements if len(ele.text) > 0 ]
    titles = [ele.text for ele in elements if len(ele.text) > 0 ]
    dates = ['' for ele in elements if len(ele.text) > 0 ]    
    
    data_china = [ (t, l, d, 'china') for (t, l, d) in zip(titles, links, dates) ]
    
    
    driver.get(base_url + '/tiaofasi/144941/index.html')
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    
    xpath = '//td[@height=23 or contains(@class, "font14")]/a[@href and @target="_blank"]'
    elements = driver.find_elements_by_xpath(xpath)
    links = [ele.get_attribute("href") for ele in elements if len(ele.text) > 0 ]
    titles = [ele.text for ele in elements if len(ele.text) > 0 ]
    dates = ['' for ele in elements if len(ele.text) > 0 ]    
    
    data_china += [ (t, l, d, 'china') for (t, l, d) in zip(titles, links, dates) ]

    driver.quit()
    
    dict_china = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_china]
  
    print (len(dict_china))

    print ('In {}, end, date is {}'.format(get_rmyh_china.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_china

def get_rmyh_jiangsu():
#     //td[@height=23 or @class="font14"]/a[@href and @target="_blank"]
    print ('In {}, begin, date is {}'.format(get_rmyh_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    base_url = 'http://nanjing.pbc.gov.cn'
    
    driver.get(base_url + '/nanjing/117512/index.html')
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    
#     print (driver.page_source)
    xpath = '//td[@class="art_titdt"]'
    elements = driver.find_elements_by_xpath(xpath)
    dates = ['' for ele in elements]    
    xpath = '//td[@class="art_titdt"]/a'
    elements = driver.find_elements_by_xpath(xpath)
    links = [ele.get_attribute("href") for ele in elements]
    titles = [ele.get_attribute("title") for ele in elements]
    
    data_jiangsu = [ (t, l, d, 'jiangsu') for (t, l, d) in zip(titles, links, dates) ]
    
    
    driver.get(base_url + '/nanjing/117532/index.html')
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    
#     print (driver.page_source)
    xpath = '//td[@class="art_titjr"]'
    elements = driver.find_elements_by_xpath(xpath)
    dates = [ele.text.replace(' ', '') for ele in elements]    
    xpath = '//td[@class="art_titjr"]/a'
    elements = driver.find_elements_by_xpath(xpath)
    links = [ele.get_attribute("href") for ele in elements]
    titles = [ele.get_attribute("title") for ele in elements]
    
    data_jiangsu += [ (t, l, d, 'jiangsu') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_jiangsu = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_jiangsu]
  
    print (len(dict_jiangsu))

    print ('In {}, end, date is {}'.format(get_rmyh_jiangsu.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_jiangsu

def get_rmyh_zhejiang():
#     //td[@height=23 or @class="font14"]/a[@href and @target="_blank"]
    print ('In {}, begin, date is {}'.format(get_rmyh_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    base_url = 'http://hangzhou.pbc.gov.cn'
    
    driver.get(base_url + '/hangzhou/125264/index.html')
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    
#     print (driver.page_source)
    xpath = '//td[@height=22]/span[2]'
    elements = driver.find_elements_by_xpath(xpath)
    dates = [ele.text for ele in elements]    
    xpath = '//td[@height=22]/span[1]/a'
    elements = driver.find_elements_by_xpath(xpath)
    links = [ele.get_attribute("href") for ele in elements]
    titles = [ele.get_attribute("title") for ele in elements]
    
    data_zhejiang = [ (t, l, d, 'zhejiang') for (t, l, d) in zip(titles, links, dates) ]
    
    
    driver.get(base_url + '/hangzhou/125249/index.html')
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    
#     print (driver.page_source)
    xpath = '//td[@height=22]/span[2]'
    elements = driver.find_elements_by_xpath(xpath)
    dates = [ele.text for ele in elements]    
    xpath = '//td[@height=22]/span[1]/a'
    elements = driver.find_elements_by_xpath(xpath)
    links = [ele.get_attribute("href") for ele in elements]
    titles = [ele.get_attribute("title") for ele in elements]
    
    data_zhejiang += [ (t, l, d, 'zhejiang') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_zhejiang = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_zhejiang]
  
    print (len(dict_zhejiang))

    print ('In {}, end, date is {}'.format(get_rmyh_zhejiang.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_zhejiang

def get_rmyh_guangdong():
#     //td[@height=23 or @class="font14"]/a[@href and @target="_blank"]
    print ('In {}, begin, date is {}'.format(get_rmyh_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    base_url = 'http://guangzhou.pbc.gov.cn'
    
    driver.get(base_url + '/guangzhou/129136/index.html')
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    
    xpath = '//td[contains(@class, "font14")]'
    elements = driver.find_elements_by_xpath(xpath)
    dates = [ele.text[-10:] for ele in elements]   
    xpath = '//td[contains(@class, "font14")]/a'
    elements = driver.find_elements_by_xpath(xpath)
    links = [ele.get_attribute("href") for ele in elements]
    titles = [ele.text for ele in elements]
    
    data_guangdong = [ (t, l, d, 'guangdong') for (t, l, d) in zip(titles, links, dates) ]
    
    
    driver.get(base_url + '/guangzhou/129138/index.html')
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    
    xpath = '//td[contains(@class, "font14")]'
    elements = driver.find_elements_by_xpath(xpath)
    dates = [ele.text[-10:] for ele in elements]   
    xpath = '//td[contains(@class, "font14")]/a'
    elements = driver.find_elements_by_xpath(xpath)
    links = [ele.get_attribute("href") for ele in elements]
    titles = [ele.text for ele in elements]
    
    data_guangdong += [ (t, l, d, 'guangdong') for (t, l, d) in zip(titles, links, dates) ]
    
    dict_guangdong = [{'pos':x[3], 'title': x[0], 'link': x[1], 'date': x[2]} for x in data_guangdong]
  
    print (len(dict_guangdong))
    
    print ('In {}, end, date is {}'.format(get_rmyh_guangdong.__name__, time.strftime('%Y-%m-%d-%H:%M', time.localtime(time.time()))))

    return dict_guangdong


def get_table(name):
    import random
    poses = ['china', 'guangdong', 'zhejiang', 'jiangsu']
    random.shuffle(poses)
    for pos in poses:
        try:
            db = pymysql.connect(host='119.29.190.115', user='impulse', password='njuacmicpc',
                         port=3306, db='gov', write_timeout = 6, read_timeout = 6)
            cursor = db.cursor()
            for dic in globals()['get_{}_{}'.format(name, pos)]():
                sql_insert(db=db,cursor=cursor,data=dic,table=name)
        except Exception as err:
            pass
        finally:    
            if db:
                db.close()

def run():
    import random
    tables = [ 'wms', 'swb','nyj', 'zscqj', 'jbw', 'zjh', 'yjh', 'rmyh']
    random.shuffle(tables)
    for tab in tables:
        try:
            get_table(tab)
        except Exception as err:
            print("Error {}".format(err))
            time.sleep(5)

if __name__ == '__main__':
    run()