# coding: utf-8
import pandas as pd
import os
import numpy as np
from random import randint
from urllib import request
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
#from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from stem.control import Controller
from stem import Signal


# Load data
# signal TOR for a new connection
def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate('scrape')
        controller.signal(Signal.NEWNYM)
        controller.close()

def text_scraper(accounts, links_subdir, text_subdir, chromedriver_dir):
    for oa in accounts:
        if oa + ".csv" not in os.listdir(links_subdir):
            print(oa + " links not found.")
            continue
        temp = pd.read_csv("{}/{}.csv".format(links_subdir, oa))
        if oa + "_text.csv" in os.listdir(path=text_subdir):
            df_text = pd.read_csv("{}/{}_text.csv".format(text_subdir, oa))
            df_text = df_text[(df_text.Text != "")]
            df_text = df_text[df_text.Text.notnull()]
            if len(df_text) == len(temp):
                print("skipped " + oa)
                continue
            else:
                title = [x for x in df_text.Title.values]
                meta = [x for x in df_text.Meta.values]
                text = [x for x in df_text.Text.values]
                URL = [x for x in df_text.URL.values]
                urls = [x for x in temp.url.values if x not in URL]
        else:
            title = []
            meta = []
            text = []
            URL = []
            urls = temp.url.values
        #url = temp.url.values[0]
        PROXY = "socks5://localhost:9050"  # IP:PORT or HOST:PORT
        chrome_options = Options()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        #chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(chromedriver_dir, options=chrome_options)  # creates a headless firefox browser
        driver.set_page_load_timeout(60)
        # js_article > div.rich_media_area_primary.video_channel.rich_media_area_primary_full
        print("Starting " + oa)
        for n in tqdm(range(len(urls))):
            if n in URL:
                print("URL already scraped")
                continue
            #url = "https://mp.weixin.qq.com/s?__biz=MjM5NDE1MDYyMQ==&amp;mid=2651120643&amp;idx=4&amp;sn=ba1a42aa9c4dd942d30ce8c6ef473d96&amp;chksm=bd7c65b18a0beca774524e1fdd857cc6fe9b9c3bbb2625b286c9b8b3245c96a1a51d9550b002&amp;scene=27#wechat_redirect"
            url = urls[n]
            try:
                driver.get(url)  # Navigates to the supplied URL
                if len(driver.find_elements_by_css_selector("#js_article > div.rich_media_area_primary.video_channel.rich_media_area_primary_full")) > 0:
                    title.append(driver.find_element_by_class_name("common_share_title").text)
                    meta.append(driver.find_element_by_class_name("flex_context").text)
                    text.append(driver.find_element_by_class_name("share_mod_context").text)
                else:
                    title.append(driver.find_element_by_class_name("rich_media_title").text)
                    meta.append(driver.find_element_by_class_name("rich_media_meta_list").text)
                    text.append(driver.find_element_by_class_name("rich_media_content").text)
            except Exception as e:
                print(e)
                title.append(np.nan)
                meta.append(np.nan)
                text.append(np.nan)
            URL.append(url)
            dat = pd.DataFrame({"ID": list(range(len(title))),
                                "Title": title,
                                "Meta": meta,
                                "Text": text,
                                "URL": URL})
            dat.to_csv("{}/{}_text.csv".format(text_subdir, oa))
            renew_connection()
            sleep(randint(4,6))
        driver.close()
        dat = pd.DataFrame({"ID" : list(range(len(title))),
                            "Title" : title,
                            "Meta" : meta,
                            "Text" : text,
                            "URL" : URL})
        dat.to_csv("{}/{}_text.csv".format(text_subdir, oa))
        print(oa + " scraped successfully.")


if __name__ == "__main__":
    directory = "/home/patrick/Dropbox/wechat_scraping/02_data"
    links_subdir = "02_links"
    text_subdir = "03_text"
    chromedriver_dir = '/usr/local/bin/chromedriver'
    os.chdir(directory)
    df = pd.read_excel("01_metadata/wechat_metadata.xlsx")
    text_scraper(accounts=df.Chinese.values,
                 links_subdir=links_subdir,
                 text_subdir=text_subdir,
                 chromedriver_dir=chromedriver_dir)


