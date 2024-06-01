# coding: utf-8
import json
import os
import random
import time
from pprint import pprint
import numpy as np
import math
import pandas as pd
from wechatarticles import ArticlesInfo
from wechatarticles.utils import get_history_urls, verify_url
#from gi.repository import Notify
import subprocess


#Notify.init("WeChat Scraper")

# 快速获取大量文章urls（利用历史文章获取链接）

# Parameters

def save_xlsx(fj, lst, ai, loc):
    if ai != None:
        df = pd.DataFrame(lst, columns=["url", "title", "date", "read_num", "like_num"])
    else:
        df = pd.DataFrame(lst, columns=["url", "title", "date"])
    df.to_csv(loc + "/" + fj + ".csv", encoding="utf-8")
    #df.to_excel("/Users/test01/Desktop/" + fj + ".xlsx", encoding="utf-8")
    print(df)

def isnan(value):
    try:
        import math
        return math.isnan(float(value))
    except:
        return False

def demo(lst, fj, ai = None, loc = None):
    # 抓取示例，供参考，不保证有效
    #fj = "北美留学生日报"
    item_lst = []
    url_title_lst = []
    for sublst in lst:
        for line in sublst:#i, line in enumerate(sublst, 0):
            item = line
            timestamp = item["comm_msg_info"]["datetime"]
            ymd = time.localtime(timestamp)
            date = "{}-{}-{}".format(ymd.tm_year, ymd.tm_mon, ymd.tm_mday)
            infos = item["app_msg_ext_info"]
            url_title_lst += [[infos["content_url"], infos["title"], date]]
            if "multi_app_msg_item_list" in infos.keys():
                url_title_lst += [
                    [info["content_url"], info["title"], date]
                    for info in infos["multi_app_msg_item_list"]
                ]

    for url, title, date in url_title_lst:
        try:
            print(url)
            if not verify_url(url):
                continue
            # 获取文章阅读数在看点赞数
            if ai != None:
                read_num, like_num, old_like_num = ai.read_like_nums(url)
                print(read_num, like_num)
                item_lst.append([url, title, date, read_num, like_num])
            else:
                item_lst.append([url, title, date])
            time.sleep(random.randint(7, 11))
        except Exception as e:
            print(e)
            #flag = 1
            break
        finally:
            save_xlsx(fj, item_lst, ai=ai, loc=loc)
    save_xlsx(fj, item_lst, ai=ai, loc=loc)

def wechat_scrape(biz = None, name = None, uin = None, end_num = 1000, likes = False, loc = None):
    if name + ".csv" in files:
        print(name + " has already been scraped")
        return 
    subprocess.Popen(['notify-send', "Started Scraping " + name + ". Key needed."])
    key = input("Enter key for " + name + ": ")
    if likes == True:
        appmsg_token = input("Enter appmsg_token for " + name + ": ")
        cookie = input("Enter cookie for " + name + ": ")
    try:
        lst = get_history_urls(
            biz, uin, key, lst=[], start_timestamp=0, start_count=0, end_count=end_num
        )
        if likes == True:
            ai = ArticlesInfo(appmsg_token, cookie)
        if len(lst) == 0:
            print("No articles successfully scraped")
            return
        else:
            ai = None
        print("抓取到的文章链接")
        demo(lst, fj=name, ai=ai, loc=loc)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    directory = "/home/harry/Dropbox/wechat_scraping/02_data"
    link_subdir = "02_links"
    os.chdir(directory)
    files = os.listdir(link_subdir)
    accounts = pd.read_excel("01_metadata/wechat_metadata.xlsx")
    names = accounts.Chinese.values
    bizs = accounts.biz.values
    uin = "MzYyOTk4MTE5OA=="
    for v in range(len(names)):
        print(names[v])
        wechat_scrape(name=names[v], biz=bizs[v], uin = uin, end_num=5000, loc=link_subdir)
