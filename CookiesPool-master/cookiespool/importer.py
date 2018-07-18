import requests

from cookiespool.db import RedisClient

conn = RedisClient('accounts', 'weibo')

def set(account, sep='----'):
    username, password = account.split(sep)
    result = conn.set(username, password)
    print('账号', username, '密码', password)
    print('录入成功' if result else '录入失败')


def scan():
    print('请输入账号密码组, 输入exit退出读入')
    while True:
        account = input()
        if account == 'exit':
            break
        set(account)

def autoscan():
    for line in open("/home/impulse/Scrapy/card1.txt"):
        set(line)
    
if __name__ == '__main__':
    scan()
