import requests
import json 

SB_CLIENT_ID = "Python Safebrowsing"
SB_CLIENT_VER = "1.0.0"


class SafebrowsingLookup(object):

    
    def __init__(self, apikey):

        self.apiurl = 'https://safebrowsing.googleapis.com/v4/threatMatches:find?key=%s' % (apikey)
        self.platform_types = ['ANY_PLATFORM']
        self.threat_types = ['THREAT_TYPE_UNSPECIFIED',
                             'MALWARE', 
                             'SOCIAL_ENGINEERING', 
                             'UNWANTED_SOFTWARE', 
                             'POTENTIALLY_HARMFUL_APPLICATION']
        self.threat_entry_types = ['URL']

    def set_threat_types(self, threats):

        self.threat_types = threats

    def set_platform_types(self, platforms): 
        
        self.platform_types = platforms

    def threat_matches_find(self, *urls): 
     
        threat_matches = []
        results = {}
 
        for url_ in urls: 
            url = {'url': url_} 
            threat_matches.append(url)
 
        request= {
            'client': {
                 'clientId': SB_CLIENT_ID,
                 'clientVersion': SB_CLIENT_VER
            },
            'threatInfo': {
                'threatTypes': self.threat_types,
                'platformTypes': self.platform_types,
                'threatEntryTypes': self.threat_entry_types,
                'threatEntries': threat_matches
            }
        }
    
        try:
            headers = {'Content-Type': 'application/json'}
        
            r = requests.post(self.apiurl, 
                            data=json.dumps(request), 
                            headers=headers)
            return r.json()
        except requests.exceptions.RequestException as e:  
            print(e) 


class UpdateAPI(object):


    def __init__(self, apikey):
        pass