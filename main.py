#!/usr/bin/env python
# Copyright (c) 2017 @x0rz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
import re
import configparser
import certstream
import entropy
import tqdm
import yaml
import sqlite3
import time
import pymongo
import socket
import json

import requests
from sitereview import SiteReview
import safebrowsing

from pydnsbl import DNSBLChecker

from bson.binary import Binary
from Levenshtein import distance
from termcolor import colored, cprint
from tld import get_tld
from urlscan import UrlScan
from confusables import unconfuse
from tldextract import extract
from slackclient import SlackClient


config = configparser.ConfigParser()
config.read('config.ini')

channel = config.get('slack', 'channel')
slack_score = int(config.get('slack', 'relevant_score'))
slack_integration = int(config.get('slack', 'integration'))
vt_key = config.get('apikeys', 'vt_key')
urlscan_key = config.get('apikeys', 'urlscan_key')

myclient = pymongo.MongoClient(config.get("mongodb", "my_instance"))
mydb = myclient[config.get("mongodb", "my_db")]
mycol = mydb[config.get("mongodb", "my_col")]

slack_token = config.get('slack', 'bot_key')
sc = SlackClient(slack_token)

certstream_url = 'wss://certstream.calidog.io'

pbar = tqdm.tqdm(desc='certificate_update', unit='cert')

def get_ip(domain):
        info = socket.getaddrinfo(domain, None)[0]
        ip_addr = info[4][0]
        if info[0] == socket.AF_INET6:
            ip_addr = re.sub(r'^0*', '', ip_addr)
            ip_addr = re.sub(r':0*', ':', ip_addr)
            ip_addr = re.sub(r'::+', '::', ip_addr)
        return ip_addr

def dnsbl_check(domain, domain_ip):
    checker = DNSBLChecker()
    output = checker.check_ip(domain_ip)
    result = str(output)
    result = result.replace("<","").replace(">","").replace("DNSBLResult",'"dnsblresult"').replace(":",':"').replace(")",')"')
    site_record = { "certphisher_site":  domain}
    response_data = { "$set": {"dnsbl": "{" + result +"}" }}
    mycol.update_one(site_record, response_data)

def urlhaus_url_check(domain, siteid):
    url = 'https://urlhaus-api.abuse.ch/v1/url/'
    params = {'url': "https://"+domain }
    response = requests.post(url, data=params)    
    json_response = response.json()
    site_record = { "_id":  siteid }
    response_data = { "$set": {"urlhaus": {"url_check": json_response }}}
    mycol.update_one(site_record, response_data)
    
def urlhaus_domain_check(domain, domain_ip, siteid):
    url = 'https://urlhaus-api.abuse.ch/v1/host/'
    params = {'host':  domain}
    response = requests.post(url, data=params)    
    json_response = response.json()
    site_record = { "_id":  siteid }
    response_data = { "$set": {"urlhaus": {"domain_check": json_response }}}
    mycol.update_one(site_record, response_data)
    
def urlhaus_host_check(domain, domain_ip, siteid):
    url = 'https://urlhaus-api.abuse.ch/v1/host/'
    params = {'host': domain_ip}
    response = requests.post(url, data=params)    
    json_response = response.json()
    site_record = { "_id":  siteid }
    response_data = { "$set": {"urlhaus": {"host_check": json_response }}}
    mycol.update_one(site_record, response_data)

    
def vt_scan(domain, siteid):
    time.sleep(26)
    url = 'https://www.virustotal.com/vtapi/v2/url/scan'
    params = {'apikey': vt_key, 'url': "https://"+ domain}
    response = requests.post(url, data=params)
    json_response = response.json()
    #check for 204, wait and try again
    if (json_response.get('response_code')) == 1:
        json_response = response.json()
        site_record = { "_id":  siteid }
        response_data = { "$set": {"virus_total": json_response }}
        mycol.update_one(site_record, response_data)
        update_check_flag(siteid, "checked_vt", "true")
    else:
        print("upload failed.")
      
    return json_response.get("permalink")
def get_domain_tld(domain):
    td, tsu = extract("https://"+domain) # prints domain, tld
    url = td + '.' + tsu # will prints as hostname.com       
    return url

def vt_domain_report(domain, siteid):
    url = get_domain_tld(domain)
    vt_url = 'https://www.virustotal.com/vtapi/v2/domain/report'
    params = {'apikey': vt_key,'domain':  domain}
    response = requests.get(vt_url, params=params)
 

def vt_report(domain, siteid):
    url = 'https://www.virustotal.com/vtapi/v2/url/report'
    params = {'api_key': vt_key, 'resource':  domain, 'allinfo': 'true', 'scan': 1}
    json_response = requests.get(url, params=params)
    print(json_response)

def urlscan_io(domain, siteid):
    u = UrlScan(urlscan_key,"https://"+ domain,public=False)
    scanid = u.submit()

    site_record = { "_id":  siteid }
    response_data = { "$set": {"urlscan_permalink": "https://urlscan.io/result/"+scanid, "urlscan_uuid":"https://urlscan.io/screenshots/"+scanid}}
    mycol.update_one(site_record, response_data)

    reportpage = "https://urlscan.io/result/"+scanid
    return reportpage

def update_record(domain, scan_id, scan_date, permalink):
    site_record = { "certphisher_site": domain }
    response_data = { "$set": {"scan_id": scan_id, "scan_date": scan_date, "permalink": permalink}}
    mycol.update_one(site_record, response_data)

def update_check_flag(siteid, flag, flag_value):
    myquery = { "_id":  siteid }
    newvalues = { "$set": { flag: flag_value }}
    mycol.update_one(myquery, newvalues)

def sitereview_check(domain, siteid):
    s = SiteReview()
    response = s.sitereview("https://"+ domain)
    s.check_response(response)
    site_record = { "_id":  siteid }
    response_data = { "$set": {"sitereview_bluecoat": {"url": s.url, "category": s.category }}}
    mycol.update_one(site_record, response_data)

def save_url(domain, score, ca):
    mydict = { "certphisher_site":  domain.lower(), "certphisher_score": score , "certificate_authority": ca,  "checked_vt": "false" , "vt_report_saved": "false"}
    site = mycol.insert_one(mydict)
    
    #host_ip = get_ip(domain)
    #urlhaus_host_check(domain, host_ip, site.inserted_id)
    #dnsbl_check(domain, host_ip)
    urlhaus_url_check(domain, site.inserted_id)
    #sitereview_check( domain, site.inserted_id)
    permalink = vt_scan( domain, site.inserted_id)
    reportpage = urlscan_io(domain, site.inserted_id)
    if slack_integration:
        if score >= slack_score:
            send_slack_message(domain, score, ca, permalink, reportpage)
    

    #vt_domain_report(domain, siteid)
    return True

def score_domain(domain):
    """Score `domain`.
    The highest score, the most probable `domain` is a phishing site.
    Args:
        domain (str): the domain to check.
    Returns:
        int: the score of `domain`.
    """
    score = 0
    for t in suspicious['tlds']:
        if domain.endswith(t):
            score += 20

    # Higher entropy is kind of suspicious
    score += int(round(entropy.shannon_entropy(domain)*50))

    # Remove lookalike characters using list from http://www.unicode.org/reports/tr39
    domain = unconfuse(domain)

    words_in_domain = re.split("\W+", domain)

    # Remove initial '*.' for wildcard certificates bug
    if domain.startswith('*.'):
        domain = domain.replace("*.","")

        # ie. detect fake .com (ie. *.com-account-management.info)
        if words_in_domain[0] in ['com', 'net', 'org']:
            score += 10

    # Testing keywords
    for word in suspicious['keywords']:
        if word in domain:
            score += suspicious['keywords'][word]

    # Testing Levenshtein distance for strong keywords (>= 70 points) (ie. paypol)
    for key in [k for (k,s) in suspicious['keywords'].items() if s >= 70]:
        # Removing too generic keywords (ie. mail.domain.com)
        for word in [w for w in words_in_domain if w not in ['email', 'mail', 'cloud']]:
            if distance(str(word), str(key)) == 1:
                score += 70

    # Lots of '-' (ie. www.paypal-datacenter.com-acccount-alert.com)
    if 'xn--' not in domain and domain.count('-') >= 4:
        score += domain.count('-') * 3

    # Deeply nested subdomains (ie. www.paypal.com.security.accountupdate.gq)
    if domain.count('.') >= 3:
        score += domain.count('.') * 3

    return score

def callback(message, context):
    """Callback handler for certstream events."""
    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        #all_domains = message['data']['leaf_cert']['all_domains']
        # Checking the subject Alt Names as it contains more urls than all_domains and more info
        all_domains = message['data']['leaf_Cert']['extensions']['subjectAltName']
        all_domains = all_domains.replace('DNS:','')
        all_domains = all_domains.split(",")
        ca = message['data']['chain'][0]['subject']['CN']
            
        for domain in all_domains:
            if "STH" in domain:
                continue
            domain = domain.replace("*.","")
            pbar.update(1)
            
            score = score_domain(domain)
            # If issued from a free CA = more suspicious
            if "Let's Encrypt" in message['data']['chain'][0]['subject']['aggregated']:
                score += 10

            if score >= 100:
                tqdm.tqdm.write(
                    "[!] Suspicious: "
                    "{} (score={})".format(colored(domain, 'red', attrs=['underline', 'bold']), score))
                save_url(domain, score, ca )
            elif score >= 90:
                tqdm.tqdm.write(
                    "[!] Likely: "
                    "{} (score={})".format(colored(domain, 'red', attrs=['underline']), score))
                save_url(domain, score, ca )
            elif score >= 80:
                tqdm.tqdm.write(
                    "[!] Likely    : "
                    "{} (score={})".format(colored(domain, 'yellow', attrs=['underline']), score))
            
        
def send_slack_message(domain, score, ca, permalink, reportpage):
    #Send message in channel

    message = ":information_source: *New suspicious Domain found:*\n *>>> "+ domain.replace(".","[.]") +" <<< with score: [" + str(score) + "]*\n - Urlscan io result *<  "+reportpage+"  >*\n\n - Virustotal result: *< "+permalink+"  >*"
    
    try:
        sc.api_call(
            "chat.postMessage",
            channel="#" + channel,
            text=message
        )
    except:
        print("Debug: Error in send_to_slack.")


if __name__ == '__main__':
    with open('suspicious.yaml', 'r') as f:
        suspicious = yaml.safe_load(f)

    with open('external.yaml', 'r') as f:
        external = yaml.safe_load(f)

    if external['override_suspicious.yaml'] is True:
        suspicious = external
    else:
        if external['keywords'] is not None:
            suspicious['keywords'].update(external['keywords'])

        if external['tlds'] is not None:
            suspicious['tlds'].update(external['tlds'])

    
    #create_connection("certphisher.db") 
    certstream.listen_for_events(callback, url=certstream_url)
