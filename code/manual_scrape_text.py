import pandas as pd
import numpy as np
import sys
import os
import random
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from stem import Signal
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate('secret')
        controller.signal(Signal.NEWNYM)

def get_ip():
    PROXY = "socks5://localhost:9050"  # IP:PORT or HOST:PORT
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % PROXY)
    service = ChromeService(executable_path=chromedriver_dir)
    driver = webdriver.Chrome(service = service, options = options)
    driver.get("http://httpbin.org/ip")
    ip = driver.find_element(By.XPATH, "/html/body/pre").text.split(":")[-1]
    ip = ip.replace("\"", "")
    driver.close()
    return(ip)

def renew_ip():
    old_ip = get_ip()
    new_ip = old_ip
    while new_ip == old_ip:
        time.sleep(1)
        renew_connection()
        new_ip = get_ip()

def scrape_account(accounts, links_subdir, text_subdir, chromedriver_dir):
    for name in accounts:
        if name + ".xlsx" not in os.listdir(links_subdir):
            print(name + "links not found")
            continue
        temp = pd.read_excel("{}/{}.xlsx".format(links_subdir, name))
        if name + "_text.csv" in os.listdir(path=text_subdir):
            df_text = pd.read_csv("{}/{}_text.csv".format(text_subdir, name))
            df_text = df_text[(df_text.Text != "")]
            df_text = df_text[df_text.Text.notnull()]
            if len(df_text) == len(temp):
                print("skipped " + name)
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
        PROXY = "socks5://localhost:9050"  # IP:PORT or HOST:PORT
        options = webdriver.ChromeOptions()
        options.add_argument('--proxy-server=%s' % PROXY)
        service = ChromeService(executable_path=chromedriver_dir)
        driver = webdriver.Chrome(service = service, options = options)
        for n in tqdm(range(len(urls))):
            url = urls[n]            
            if url in URL:
                print("URL already scraped")
                continue
            try:
                driver.get(url)  # Navigates to the supplied URL
                for count in range(6):
                    if len(driver.find_elements(By.CLASS_NAME, 'common_share_title')) > 0 or len(driver.find_elements(By.CLASS_NAME, 'rich_media_title')) > 0:
                        break
                    else:
                        time.sleep(2)
                    if count % 2 == 1:
                        driver.get(url)        
                if len(driver.find_elements(By.CSS_SELECTOR, "#js_article > div.rich_media_area_primary.video_channel.rich_media_area_primary_full")) > 0:
                    title.append(driver.find_element(By.CLASS_NAME, "common_share_title").text)
                    meta.append(driver.find_element(By.CLASS_NAME, "flex_context").text)
                    text.append(driver.find_element(By.CLASS_NAME, "share_mod_context").text)
                else:
                    title.append(driver.find_element(By.CLASS_NAME, "rich_media_title").text)
                    meta.append(driver.find_element(By.CLASS_NAME, "rich_media_meta_list").text)
                    text.append(driver.find_element(By.CLASS_NAME, "rich_media_content").text)
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
            dat.to_csv("{}/{}_text.csv".format(text_subdir, name))
            renew_connection()
            if n % 5 == 0:
                print("renewing IP address")
                renew_ip()
            time.sleep(random.randint(4,6))
        driver.close()

if __name__ == "__main__":
    chromedriver_dir = '/usr/local/bin/chromedriver'
    
    directory = os.path.dirname(os.getcwd()) + "/datasets"
    os.chdir(directory)
    links_subdir = "links"
    text_subdir = "texts"
    accounts = ["北美留学生日报"]
    scrape_account(accounts = accounts,
                   links_subdir = links_subdir,
                   text_subdir = text_subdir,
                   chromedriver_dir = chromedriver_dir)

