import pandas as pd
import numpy as np
import sys
import os
import subprocess
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

def renew_tor_ip():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate('secret')
        controller.signal(Signal.NEWNYM)
        #time.sleep(controller.get_newnym_wait())

def scrape_text(name, link_subdir, text_subdir, chromedriver_dir):
    link_file_path = "{}/{}.csv".format(link_subdir, name)
    text_file_path = "{}/{}_text.csv".format(text_subdir, name)
    df_link = pd.read_csv(link_file_path)
    if name + "_text.csv" in os.listdir(path=text_subdir):
        df_text = pd.read_csv("{}/{}_text.csv".format(text_subdir, name))
        df_text = df_text[(df_text.Text != "")]
        df_text = df_text[df_text.Text.notnull()]
        if len(df_text) == len(df_link):
            print("skipped " + name)
            continue
        else:
            title = [x for x in df_text.Title.values]
            meta = [x for x in df_text.Meta.values]
            text = [x for x in df_text.Text.values]
            URL = [x for x in df_text.URL.values]
            urls = [x for x in df_link.url.values if x not in URL]
    else:
        title = []
        meta = []
        text = []
        URL = []
        urls = df_link.url.values
    PROXY = "socks5://localhost:9050" # IP:PORT or HOST:PORT
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % PROXY)
    service = ChromeService(executable_path=chromedriver_dir)
    browser = webdriver.Chrome(service = service, options = options)
    browser.set_page_load_timeout(60)
    print("working fine")
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
        if n % 5 == 0:
            print("renewing IP address")
            renew_ip()
        time.sleep(random.randint(3,6))
        driver.close()

def get_ip():
    PROXY = "socks5://localhost:9050" # IP:PORT or HOST:PORT
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % PROXY)
    service = ChromeService(executable_path=chromedriver_dir)
    browser = webdriver.Chrome(service = service, options = options)
    browser.get("http://httpbin.org/ip")
    ip = browser.find_element(By.XPATH, "/html/body/pre").text.split(":")[-1]
    ip = ip.replace("\"", "")
    #time.sleep(1)
    renew_connection()
    #time.sleep(1)
    browser.close()
    return(ip)

def test_ip():
    ip = ""
    old_ip = ""
    for i in tqdm(range(2)):
        while ip == old_ip:
            ip = get_ip()
        print(ip)
        old_ip = ip


if __name__ == "__main__":
    #directory = os.path.dirname(os.getcwd()) + "/02_data"
    #link_subdir = "02_links"
    #text_subdir = "03_text"
    #os.chdir(directory)
    chromedriver_dir = '/usr/local/bin/chromedriver'
    #files = os.listdir(link_subdir)
    #accounts = pd.read_excel("01_metadata/wechat_metadata.xlsx")
    #names = accounts.Chinese.values
    #for name in names:
    #    if name + ".csv" not in files:
    #        print(name + "links not yet scraped")
    #    else:
    #        scrape_text(name = name, link_subdir = link_subdir, text_subdir = text_subdir, chromedriver_dir = chromedriver_dir)
    test_ip()