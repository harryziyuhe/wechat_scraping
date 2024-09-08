import wechat_scrape_links
import os
from utils import *
import requests
import re
import datetime
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import pandas as pd
import random

date_time_pattern = re.compile(r'var create_time = "(\d+)"')
global_params = None
account_name = ""
offset = 0
count = 0
df_article = None
continue_flag = 1

def get_params():
    global global_params
    if os.path.exists("params.json"):
        json_params = open("params.json", "r", encoding="utf-8")
        params = json.load(json_params)
        global_params = UserData.fromJson(params)
        json_params.close()

def initialize():
    global offset
    global count
    if os.path.exists("params.json"):
        os.remove("params.json")
    offset = 0
    count = 0

def get_links(user: UserData, tor = True):
    global continue_flag
    url = f"https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&f=json&count=20&is_ok=1&__biz={user.biz}&key={user.key}&uin={user.uin}&pass_ticket={user.pass_ticket}&offset={offset}"
    session = get_tor_session(tor)
    msg_json = session.get(url, headers=user_head(global_params), verify=False).json()
    if (('can_msg_continue' in msg_json) and msg_json['can_msg_continue'] != 1):
        continue_flag = 0
    if "general_msg_list" in msg_json.keys():
        url_list = json.loads(msg_json['general_msg_list'])['list']
        return url_list
    return []

def check_existing(article_detail: ArticleData):
    global df_article
    return((df_article['title'] == article_detail.title).any())

def parse_entry(user: UserData, article_detail: ArticleData, entry, tor = True):
    global offset
    global count
    if "app_msg_ext_info" in entry:
        entry = entry["app_msg_ext_info"]
        flag = get_article(user, article_detail, entry, tor)
        if flag == "LinkError":
            print(f"Link Error: {entry}")
        if flag == "Scraped":
            print("Some articles have been scraped")
            return flag
        count += 1
        if "multi_app_msg_item_list" in entry:
            sublist = entry["multi_app_msg_item_list"]
            print("Sub-articles detected")
            for item in sublist:
                flag = get_article(user, article_detail, item, tor)
                if flag == "LinkError":
                    print(f"Link Error: {item}")
                count += 1
    else:
        print("No title")

def get_article(user: UserData, article_detail: ArticleData, entry, tor = True):
    global df_article
    if "title" in entry:
        article_detail.title = entry['title']
        article_detail.link = entry['content_url'].replace("amp;", "")
        article_detail.author = entry['author']
    else:
        return("LinkError")
    if check_existing(article_detail):
        return("Scraped")
    get_content(article_detail, tor)
    get_stats(article_detail, user, tor)
    df_article = pd.concat([df_article, pd.DataFrame([vars(article_detail)])], ignore_index=True)
    time.sleep(random.randint(2,5))
    
def get_content(article_detail: ArticleData, tor = True):
    session = get_tor_session(tor)
    response = session.get(article_detail.link, headers=general_head, verify=False, timeout=(10, 10))
    soup = BeautifulSoup(response.text, 'html.parser')

    # get article content
    article_text = soup.find(id="js_content")
    
    if article_text is None:
        article_text = soup.find(id="page_content")
    
    if article_text:
        article_text = article_text.get_text()
    else:
        print("No element was found.")
    
    content = '\n'.join([text.strip() for text in article_text if text.strip()])
    article_detail.content = content

    # get article published date
    create_time = ""
    match = date_time_pattern.search(response.text)
    if match:
        timestamp = int(match.group(1))
        # Convert the timestamp to a datetime object
        create_time = datetime.datetime.fromtimestamp(timestamp)
    article_detail.time = create_time

def get_stats(article_detail: ArticleData, user: UserData, tor = True):
    session = get_tor_session(tor)
    read_num, like_num = 0, 0
    query_params = parse_qs(urlparse(article_detail.link).query)
    mid = query_params['mid'][0]
    sn = query_params['sn'][0]
    idx = query_params['idx'][0]
    detailUrl = f"https://mp.weixin.qq.com/mp/getappmsgext?f=json&mock=&fasttmplajax=1&uin={user.uin}&key={user.key}&pass_ticket={user.pass_ticket}"
    response = session.post(detailUrl, headers=user_head(user),
                             data=article_data(user, mid, sn, idx), verify=False).json()
    if "appmsgstat" in response:
        info = response['appmsgstat']
        read_num = info['read_num']
        like_num = info['old_like_num']
        article_detail.read = read_num
        article_detail.like = like_num

def run(tor = True):
    global global_params
    global offset
    global count
    global df_article
    global continue_flag
    initialize()
    while True:
        get_params()
        if global_params != None:
            print("Parameters detected")
            account_name = get_account_name(global_params)
            print(f"Start scraping {account_name}")
            break
        else:
            time.sleep(1)
            print("Detecting")
            continue

    if os.path.exists(f"data/{account_name}.csv"):
        df_article = pd.read_csv(f"data/{account_name}.csv")
        offset_plus = len(df_article)
    else:
        df_article = pd.DataFrame(columns = ["author", "title", "content", "link", "read", "like", "time"])
    
    while True:
        url_list = get_links(global_params, tor)
        if len(url_list) == 0:
            #refresh()
            #url_list = get_links(global_params, tor)
            if len(url_list) == 0:
                print("Parameter error, verify account status")
        for entry in url_list:
            article_detail = ArticleData()
            flag = ""
            try:
                flag = parse_entry(global_params, article_detail, entry, tor)
            except Exception as e:
                print(e)
                print(f"Scrape Error: {entry}")
            if flag == "Scraped":
                offset += offset_plus
                break
            offset += 1
            df_article.to_csv(f"data/{account_name}.csv")
        if (continue_flag == 0) or (offset >= 1):
            print(f"Article collection completed. {count} articles collected.")
            break
        time.sleep(random.randint(2, 5))

##################################################################
# Pipeline 
# 1. Set up mitmproxy to retrieve parameters in VirtualBox (retrieve_params.py)
# 2. Initialize (initialize()) and get parameters(get_params())
# 3. Start retrieving article links (get_links())
# 4. For each entry in the links list, retrieve article information (parse_entry()), data saved in the ArticleData class
# 5. After each iteration, save article data into csv file for maximum record retention

if __name__ == "__main__":
    directory = os.getcwd()
    links_subdir = directory + "data/links"
    text_subdir = directory + "data/text"
    tor = input("Use Tor to avoid IP blocks (default is yes)? Y/n: ").upper()
    if (tor == "N") or (tor == "No"):
        tor = False
    else:
        tor = True
    run(tor)
    