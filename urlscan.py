from __future__ import print_function
import requests,json

class UrlScan:

    def __init__(self,apikey="",url="",useragent=None,referer=None,public=True):
        assert len(apikey) > 0, "API key must be defined"
        assert len(url) > 0, "Url must be defined"
        assert type(public) == type(True), "Public must be a boolean"
        self.apikey = apikey
        self.url = url
        self.useragent = useragent
        self.referer = referer
        self.public = public
        self.scanid = None

    def submit(self):
        header = {'API-Key':self.apikey}
        req = {"url":self.url}
        if self.useragent is not None:
            req['useragent'] = self.useragent
        if self.public:
            req['public'] = "on"
        if self.referer is not None:
            req['referer'] = self.referer
        s = requests.post("https://urlscan.io/api/v1/scan/",data=req,headers=header)
        if s.status_code == 200:
            self.scanid = json.loads(s.text)['uuid']
            return self.scanid
        else:
            raise Exception('Non-200 respond')

    def checkStatus(self):
        header = {'API-Key':self.apikey}
        if self.scanid is None:
            raise Exception("Scan has not been submitted yet, call submit() first")
        r = requests.get("https://urlscan.io/api/v1/result/%s/" % self.scanid,headers=header)
        if r.status_code == 200:
            return r
        if r.status_code == 404:
            raise Exception("Scan has not completed yet")

    def getResult(self):
        header = {'API-Key':self.apikey}
        if self.scanid is None:
            raise Exception("Scan has not been submitted yet, call submit() first")
        r = requests.get("https://urlscan.io/api/v1/result/%s/" % self.scanid,headers=header)
        json_response = r.json()
        if r.status_code == 404:
            raise Exception("Scan has not completed yet")
        return json_response

    def getDom(self):
        self.checkStatus()
        header = {'API-Key':self.apikey}
        dom = requests.get("https://urlscan.io/dom/%s/" % self.scanid,headers=header)
        if dom.status_code == 200:
            return dom.text
        else:
            raise Exception('Non-200 respond: %s - %s' % dom.status_code,dom.text)

    def getScreenshot(self):
        self.checkStatus()
        header = {'API-Key':self.apikey}
        screen = requests.get("https://urlscan.io/screenshots/%s.png" % self.scanid,headers=header)
        if screen.status_code == 200:
            return screen.content
        else:
            raise Exception('Non-200 respond: %s - %s' % screen.status_code,screen.text)

    def __repr__(self):
        return "<UrlScan(url='%s', useragent='%s', referer='%s', public='%s', scanid='%s'>" % (self.url,self.useragent,self.referer,self.public,self.scanid)