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
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate('secret')
        controller.signal(Signal.NEWNYM)

def get_ip():
    PROXY = "socks5://localhost:9050"  # IP:PORT or HOST:PORT
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get("http://httpbin.org/ip")
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "/html/body"))
    )
    ip = element.text.split(":")[-1].replace("\"", "").replace("}", "").replace("\n", "")
    print("IP Address:", ip)

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
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        #driver.get("http://httpbin.org/ip")
        for n in tqdm(range(len(urls))):
            url = urls[n]            
            if url in URL:
                print("URL already scraped")
                continue
            try:
                driver.get(url)  # Navigates to the supplied URL
                for count in range(6):
                    if len(driver.find_elements(By.CLASS_NAME, 'common_share_title')) > 0 or len(driver.find_elements(By.CLASS_NAME, 'rich_media_title')) > 0 or len(driver.find_elements(By.CLASS_NAME, 'weui-msg__title')) > 0:
                        break
                    else:
                        time.sleep(2)
                    if count % 2 == 1:
                        driver.get(url)
                if len(driver.find_elements(By.CLASS_NAME, 'weui-msg__title')) > 0:
                    print("Content has been deleted")
                    continue        
                if len(driver.find_elements(By.CSS_SELECTOR, "#js_article > div.rich_media_area_primary.video_channel.rich_media_area_primary_full")) > 0:
                    title.append(driver.find_element(By.CLASS_NAME, "common_share_title").text)
                    meta.append(driver.find_element(By.CLASS_NAME, "flex_context").text)
                    text.append(driver.find_element(By.CLASS_NAME, "share_mod_context").text)
                else:
                    title.append(driver.find_element(By.CLASS_NAME, "rich_media_title").text)
                    meta.append(driver.find_element(By.CLASS_NAME, "rich_media_meta_list").text)
                    if len(driver.find_elements(By.CLASS_NAME, "rich_media_content")) > 0:
                        text.append(driver.find_element(By.CLASS_NAME, "rich_media_content").text)
                    elif len(driver.find_elements(By.CLASS_NAME, "js_underline_content")) > 0:
                        text.append(driver.find_element(By.CLASS_NAME, "js_underline_content").text)
                    else:
                        text.append(np.nan)
            except Exception as e:
                print(e)
                print(url)
                title.append(np.nan)
                meta.append(np.nan)
                text.append(np.nan)
            URL.append(url)
            #print(len(title))
            #print(len(meta))
            #print(len(text))
            #print(len(URL))
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
    chromedriver_dir = '/usr/bin/chromedriver'
    directory = os.path.dirname(os.getcwd()) + "/datasets"
    os.chdir(directory)
    links_subdir = "links"
    text_subdir = "texts"
    accounts = ["北美留学生日报"]
    scrape_account(accounts = accounts,
                   links_subdir = links_subdir,
                   text_subdir = text_subdir,
                   chromedriver_dir = chromedriver_dir)

