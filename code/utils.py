import pyautogui
import time

def retrieve_key():
    f = open("/home/harry/Dropbox/wechat/01_code/key.txt", "r")
    url = f.read()
    return url


def click_account(account_name, biz, exp_key=""):
    account_lst = {
        "环球时报": "/home/harry/Dropbox/wechat/01_code/global_times.png",
        "新华网": "/home/harry/Dropbox/wechat/01_code/xinhua_news.png"
    }
    header_lst = {
        "环球时报": "/home/harry/Dropbox/wechat/01_code/global_times_header.png",
    }

    #keep clicking until __biz matches and key is new key
    x, y = pyautogui.locateCenterOnScreen(header_lst[account_name])
    while x is None or y is None:
        try:
            pyautogui.click(account_lst[account_name])
            time.sleep(3)
        except Exception as e:
            print(e)
        x, y = pyautogui.locateOnScreen(header_lst[account_name])
    y = y + 200
    while True:
        pyautogui.click(x, y)
        time.sleep(3)
        url = retrieve_key()
        key = url.split("key=")[1].split("&")[0]
        #print(key)
        if (biz in url) and (key != exp_key):
            return key
        y = y + 50

def click_links(account_name):
    account_lst = {
        "环球时报": "/home/harry/Dropbox/wechat/01_code/global_times.png",
        "新华网": "/home/harry/Dropbox/wechat/01_code/xinhua_news.png"
    }
    header_lst = {
        "环球时报": "/home/harry/Dropbox/wechat/01_code/global_times_header.png",
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