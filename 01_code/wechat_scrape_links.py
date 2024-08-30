import subprocess
import os
import time
import pandas as pd
from datetime import datetime
import requests
import sys
from tqdm import tqdm
import utils
import random

def getHead(biz, uin, key, pass_ticket):
    cookie = utils.retrieve_cookie()
    return {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; 64) AppleWebKit/537.36 (KHMTL, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9053 Flue",
        "Cookie": cookie,
        "Referer": f"https://mp.weixin.qq.com/mp/profile_ext?action=home&lang=zh_CN&__biz=${biz}&uin=${uin}&key=${key}&pass_ticket=${pass_ticket}",
        "Origin": "https://mp.weixin.qq.com"
    }

def get_url(name, biz, uin, key, pass_ticket, start_timestamp = 0, start_count = 0, end_count = sys.maxsize, return_flag = False):
    lst = []
    flag = True
    try:
        while True:
            print("getting url for ", name)
            res = scrape_urls(biz, uin, key, pass_ticket, offset = start_count)
            print("links:", res)
            if res == []:
                uin, key, pass_ticket = utils.click_account(account_name = name, biz = biz, exp_key = key)
                res = scrape_urls(biz, uin, key, pass_ticket, offset = start_count)
                if res == []:
                    subprocess.Popen(['notify-send -u critical', "Scraping Finished"])
                    break
            start_count += 10
            lst.append(res)
            dt = res[-1]["comm_msg_info"]["datetime"]
            if dt <= start_timestamp or start_count >= end_count:
                break
            time.sleep(random.randint(6, 10))
            if start_count % 100 == 0:
                print(start_count)
    except KeyboardInterrupt as e:
        flag = False
        subprocess.Popen(['notify-send -u critical', "程序手动终止"])
    except Exception as e:
        flag = False
        subprocess.Popen(['notify-send -u critical', "获取文章链接失败。。。退出程序"])
    finally:
        return lst

def scrape_urls(biz, uin, key, pass_ticket, offset = "0", cookie = "", proxies = {"http": None, "https": None}):
    s = requests.session()
    #print("open scrape session")
    #print(biz, uin, key)
    headers = {"Cookies": cookie}
    params = {
        "action": "getmsg",
        "f": "json",
        "count": "10",
        "is_ok": "1",
        "__biz": biz,
        "key": key,
        "uin": uin,
        "pass_ticket": pass_ticket,
        "offset": str(offset)
    }
    print("parameters: ", params)
    origin_url = "https://mp.weixin.qq.com/mp/profile_ext"
    full_url = f"{origin_url}?action=getmsg&f=json&count=20&is_ok=1&__biz={biz}&key={key}&uin={uin}&pass_ticket={pass_ticket}&offset={offset}"
    print(full_url)
    f = open("url.txt", "w")
    f.write(full_url)
    f.close()
    print(full_url)
    #msg_json = requests.get(full_url, headers=getHead(biz, uin, key, pass_ticket), verify=False)
    #print(msg_json)
    msg_json = s.get(
        origin_url, params = params, headers = headers, proxies = proxies
    ).json()
    print(msg_json)
    if "general_msg_list" in msg_json.keys():
        lst = [
            item
            for item in eval(msg_json["general_msg_list"])["list"]
            if "app_msg_ext_info" in item.keys()
        ]
        return lst
    return []

def verify_url(content_url = ""):
    verify_list = ["mp.weixin.qq.com", "__biz", "mid", "idx"]
    if "video?" in content_url or "show?" in content_url:
        return False
    for string in verify_list:
        if string not in content_url:
            return False
    return True

def save_to_csv(df_link = [], lst = [], name = "Untitled", loc = None):
    if loc is None:
        loc = "{}.csv".format(name)
    else:
        loc = "{}/{}.csv".format(loc, name)
    df = pd.DataFrame(columns = ["url", "title", "date"])
    for item in lst:
        for entry in item:
            timestamp = entry["comm_msg_info"]["datetime"]
            time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            infos = entry["app_msg_ext_info"]
            if not verify_url(infos["content_url"]): #check whether the url is a video
                continue
            df.loc[len(df)] = [infos["content_url"], infos["title"], time]
            if "multi_app_msg_item_list" in infos.keys(): #scrape additional articles in the same group
                for info in infos["multi_app_msg_item_list"]:
                    if not verify_url(info["content_url"]):
                        continue
                    df.loc[len(df)] = [info["content_url"], info["title"], time]
    if (not isinstance(df_link, pd.DataFrame)) or (df_link.shape[0] == 0):
        df.to_csv(loc)
    else:
        df.append(df_link).drop_duplicates().reset_index(drop = True)

def wechat_scrape(biz = None, name = None, uin = None, loc = None):
    df_link = pd.DataFrame(columns = ["url", "title", "date"])
    timestamp = 0
    print("scraping", name)
    if name + ".csv" in files:
        file_path = "{}/{}.csv".format(link_subdir, name)
        df_link = pd.read_csv(file_path)
        last_mod = df_link.date.values[0]
        modified = datetime.strptime(last_mod, "%Y-%m-%d")
        timestamp = datetime.timestamp(modified)
        now = datetime.now()
        if ((now - modified).days > 1): #do not update if account was scraped in less than 24 hours
            print(name, "has already been scraped")
            return
    subprocess.Popen(['notify-send', "Started Scraping " + name])
    uin, key, pass_ticket = utils.click_account(account_name = name, biz = biz)
    try:
        
        lst = get_url(name = name,
                      biz = biz,
                      uin = uin,
                      key = key,
                      pass_ticket = pass_ticket,
                      start_timestamp = timestamp)
        print("return url list: ", lst)
        if len(lst) == 0:
            subprocess.Popen(['notify-send', "No articles found"])
            return
        subprocess.Popen(['notify-send', "Articles Successfully Scraped"])
        save_to_csv(df_link, lst, name = name, loc = loc)
    except Exception as e:
        print(e)

def metadata_scrape(accounts, uin, loc):
    if not isinstance(accounts, pd.DataFrame):
        raise Exception("Accounts must be a DataFrame")
    if not isinstance(uin, str):
        raise Exception("Uin must be a string")
    if not os.path.exists(loc):
        raise Exception("Specified directory is not valid")
    names = accounts.Chinese.values
    bizs = accounts.biz.values
    uin = "MzYyOTk4MTE5OA=="
    for (name, biz) in zip(names, bizs):
        print(name)
        wechat_scrape(name = name, 
                      biz = biz,
                      uin = uin,
                      loc = link_subdir)

if __name__ == "__main__":
    directory = os.path.dirname(os.getcwd()) + "/02_data"
    link_subdir = "02_links"
    os.chdir(directory)
    #print(os.getcwd())
    files = os.listdir(link_subdir)
    accounts = pd.read_excel("01_metadata/wechat_metadata.xlsx")
    names = accounts.Chinese.values
    bizs = accounts.biz.values
    uin = "MjI5NDM5NTYy=="
    for (name, biz) in zip(names, bizs):
        #print(name)
        if name != "环球时报":
            print("Finished")
            break
        wechat_scrape(name = name,
                      biz = biz,
                      uin = uin,
                      loc = link_subdir)