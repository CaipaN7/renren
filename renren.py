import requests, js2py
import pymongo, time

class RenrenSpider(object):
    sess = requests.Session()

    def connect_mongo(self):
        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        db = client.Caipan
        # collection = db.renreninfo
        return db

    def js2py(self):
        t = {
            'phoneNum': '15838278051',
            'password': 'cpzaizheli131411',
            'c1': '-100'
        }
        content = js2py.EvalJs()
        content.t = t

        res = self.sess.get(url='http://activity.renren.com/livecell/rKey',
          headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Mobile Safari/537.36'})
        n = res.json()['data']
        content.n = n

        with open('setMaxDigits.js', 'r', encoding='utf-8') as f:
            content.execute(f.read())
        with open('BarrettMu.js', 'r', encoding='utf-8') as f:
            content.execute(f.read())
        with open('RSA.js', 'r', encoding='utf-8') as f:
            content.execute(f.read())

        js = '''
        t.password = t.password.split("").reverse().join(""),
        setMaxDigits(130);
        var o = new RSAKeyPair(n.e,"",n.n)
          , r = encryptedString(o, t.password);
        t.password = r,
        t.rKey = n.rkey
        '''

        content.execute(js)
        return content

    def login(self, content):
        data = {
            'phoneNum': content.t.phoneNum,
            'password': content.t.password,
            'c1': content.t.c1,
            'rKey': content.t.rKey
        }

        res = self.sess.post(url='http://activity.renren.com/livecell/ajax/clog', data=data,
    headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Mobile Safari/537.36', 'Referer': 'http://activity.renren.com/livecell/log?c1=-100&c2=&c3=&c4=&from_uid=&isFull=&QRCodeRecharge='})

    def get_info(self, url):
        res = self.sess.get(url)
        results = res.json()['roomList']['roomList']
        for result in results:
            info = {
                'name': result['name'],
                'title': result['title'],
                'charmLevel': result['charmLevel'],
                'viewtotalCount': result['viewTotalCount'],
                'cover_img': result['coverUrl'],
                'playerId': result['playerId'],
                'liveRoomId': result['liveRoomId']
            }
            self.insert_mongo(info)


    def insert_mongo(self, info):
        try:
            db = self.connect_mongo()
            if db.renreninfo.insert(info):
                pass
                # print('插入成功')
        except Exception as e:
            print('插入失败', e)

    def get_log(self, url):
        res = self.sess.get(url)
        results = res.json()['hotShares']
        for result in results:
            log = {
                'username': result['userName'],
                'title': result['title'],
                'summary': result['summary'],
                'pubdate': time.strftime('%Y-%m-%d', time.localtime(int(int(result['creationDate'])/1000))),
                'sharecount': result['shareCount'],
                'viewcount': result['viewCount'],
                'url': result['url']
            }
            print(log)


if __name__ == '__main__':
    base_url = 'http://share.renren.com/share/hotlist?t=1&curpage={}&sort=0&v=1&requestToken=1809704295&_rtk=379ee3c1'
    # base_url = 'http://activity.renren.com/outshare/getLiveRoomList?needList=1&page={}&pageSize=13&c4=0'
    spider = RenrenSpider()
    for i in range(0, 6):
        url = base_url.format(i)
        content = spider.js2py()
        spider.login(content)
        spider.get_log(url)
        # spider.get_info(url)


