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

def renew_tor_ip():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate('secret')
        controller.signal(Signal.NEWNYM)
        #time.sleep(controller.get_newnym_wait())

def scrape_text(name, link_subdir, text_subdir, chromedriver_dir):
    link_file_path = "{}/{}.csv".format(link_subdir, name)
    text_file_path = "{}/{}_text.csv".format(text_subdir, name)
    df_link = pd.read_csv(link_file_path)
    df = pd.DataFrame(
        columns = ["Title", "Meta", "Text", "URL", "Date"]
    )
    if name + "_text.csv" in os.listdir(text_subdir):
        df_text = pd.read_csv(text_file_path)
        df_text = df_text[df_text.Text.notnull()]
        df_text = df_text[df_text.Text != ""]
        if len(df_text) == len(df_link):
            print(name,"already scraped")
            return
        else:
            existing_urls = df_text.URL.values
            urls = [x for x in df_link.url.values if x not in existing_urls]
    else:
        urls = df_link.url.values
    PROXY = "socks5://localhost:9050" # IP:PORT or HOST:PORT
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % PROXY)
    service = ChromeService(executable_path=chromedriver_dir)
    browser = webdriver.Chrome(service = service, options = options)
    browser.set_page_load_timeout(60)
    print("working fine")
    for link in tqdm(urls):
        try:
            browser.get("http://httpbin.org/ip")
        except Exception as e:
            print(e)
        renew_tor_ip()

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
    renew_tor_ip()
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