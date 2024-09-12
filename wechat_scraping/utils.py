import pyautogui
import time
import os
import json
from stem import Signal
from stem.control import Controller
import requests
import pandas as pd

PROXY = "socks5://localhost:9050"

general_head = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
	"Cookie": "rewardsn=; wxtokenkey=777",
	"Sec-Ch-Ua":'Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123',
	"Sec-Ch-Ua-Platform":"\"Windows\"",
	"Sec-Fetch-Dest":"document",
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
}

tor_count = 0

class UserData:
    def __init__(self, biz, uin, key, pass_ticket, cookie):
        self.biz = biz
        self.uin = uin
        self.key = key
        self.pass_ticket = pass_ticket
        self.cookie = cookie
    
    def toJson(self):
        return {
            "biz": self.biz,
            "uin": self.uin,
            "key": self.key,
            "pass_ticket": self.pass_ticket,
            "cookie": self.cookie
        }
    
    @staticmethod
    def fromJson(data):
        return UserData(data['biz'], data['uin'], data['key'], data['pass_ticket'], data['cookie'])
    
class ArticleData:
    def __init__(self):
        self.author = ""
        self.title = ""
        self.content = ""
        self.link = ""
        self.read = ""
        self.like = ""
        self.pub_time = ""
        self.scrape_time = ""

def get_tor_session(tor = True):
    global tor_count
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    tor_count = (tor_count + 1) % 5
    if tor:
        if tor_count == 0:
            renew_connection()
        session.proxies = {'http':  'socks5://127.0.0.1:9050',
                           'https': 'socks5://127.0.0.1:9050'}
    return session

def user_head(user: UserData):
	return {
		"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
		"Connection": 'keep-alive',
		'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9053 Flue",
		"Cookie": user.cookie,
		"Referer": f"https://mp.weixin.qq.com/mp/profile_ext?action=home&lang=zh_CN&__biz=${user.biz}&uin=${user.uin}&key=${user.key}&pass_ticket=${user.pass_ticket}",
		"Origin": "https://mp.weixin.qq.com"
	}

def article_data(user: UserData, mid, sn, idx):
    return {
        "__biz": user.biz,
        "appmsg_type": 9,
        "mid": mid,
        "sn": sn,
        "idx": idx,
        "scene": 126,
        "version": "6309092b",
        "is_need_ticket": 0,
        "is_need_ad": 0,
        "reward_uin_count": 0,
        "msg_daily_idx": 1,
        "is_original": 0,
        "is_only_read": 1,
        "pass_ticket": user.pass_ticket,
    }

def get_account_name(user: UserData):
    accounts = pd.read_excel("data/wechat_metadata.xlsx")
    accounts.set_index('biz', inplace=True)
    
    if user.biz in accounts.index:
        return accounts.at[user.biz, 'Chinese']
    else:
        return ""
    
def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate('secret')
        controller.signal(Signal.NEWNYM)

def click_account(account_name, biz, exp_key=""):
    account_lst = {
        "环球时报": "/home/harry/Documents/GitHub/wechat_scraping/01_code/global_times.png",
        "新华网": "/home/harry/Documents/GitHub/wechat_scraping/01_code/xinhua_news.png"
    }
    header_lst = {
        "环球时报": "/home/harry/Documents/GitHub/wechat_scraping/01_code/global_times_header.png",
    }
    x, y = pyautogui.locateCenterOnScreen(header_lst[account_name])
    while x is None or y is None:
        try:
            pyautogui.click(account_lst[account_name])
            time.sleep(3)
        except Exception as e:
            print(e)
        x, y = pyautogui.locateOnScreen(header_lst[account_name])
    y = y + 300
    while True:
        pyautogui.click(x, y)
        time.sleep(3)
        get_params()
        if global_params != None:
            print("Official account identified, initialize scraping")
            break
        else:
            print("detecting")
        y = y + 50

def refresh(account_name):
    # Move to random location to avoid blocking refresh button
    pyautogui.moveTo(500, 500, duration=0.5)
    refresh_button = f"fig/{account_name}.png"
    print(refresh_button)
    try:
        location = pyautogui.locateOnScreen(refresh_button)
        x, y = pyautogui.center(location)
    except:
        input("Refresh button not found, verify set up and press enter.")
    pyautogui.click(x, y + 50)
    # Move to random location to avoid blocking refresh button
    pyautogui.moveTo(x + 50, y + 50, duration=0.5)
    

def click_links(account_name):
    account_lst = {
        "环球时报": "/home/harry/Documents/GitHub/wechat_scraping/01_code/global_times.png",
        "新华网": "/home/harry/Documents/GitHub/wechat_scraping/01_code/xinhua_news.png"
    }
    header_lst = {
        "环球时报": "/home/harry/Documents/GitHub/wechat_scraping/01_code/global_times_header.png",
    }
    input("Please confirm scraping set up is ready by pressing enter...")
    x, y = pyautogui.locateOnScreen(header_lst[account_name])
    while x is None or y is None:
        input("Scraping set up not ready, please set up and confirm by pressing enter...")
        x, y = pyautogui.locateOnScreen(header_lst[account_name])
    ytop = y + 50
    ybottom = y + 1000
    


#click_account("Global Times")
#print(pyautogui.position())
#pyautogui.click(1000, 565, duration=1)