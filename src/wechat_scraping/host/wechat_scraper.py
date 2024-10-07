import os, re, datetime, urllib3, random, argparse, sys, time
from src.wechat_scraping.host.utils import *
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import pandas as pd

DATE_TIME_PATTERN = re.compile(r'var create_time = "(\d+)"')
GLOBAL_PARAMS = None
ACCOUNT_NAME = ""
OFFSET = 0
COUNT = 0
DF_ARTICLE = None
CONTINUE_FLAG = 1
urllib3.disable_warnings()
params_path = os.path.join(os.path.dirname(__file__), '../virtualbox/params.json')
PASSWORD = 'secret'
VERBOSE = False

def get_params(reload = False):
    global GLOBAL_PARAMS
    global ACCOUNT_NAME
    global VERBOSE
    if os.path.exists(params_path):
        os.remove(params_path)
    if reload:
        refresh(ACCOUNT_NAME)
    if VERBOSE:
        print('Detecting...')
    while True:
        if os.path.exists(params_path):
            json_params = open(params_path, "r", encoding = "utf-8")
            params = json.load(json_params)
            GLOBAL_PARAMS = UserData.fromJson(params)
            json_params.close()
            if GLOBAL_PARAMS != None:
                print("Parameters detected")
                break
        time.sleep(1)

def initialize():
    global OFFSET
    global COUNT
    global GLOBAL_PARAMS
    global ACCOUNT_NAME
    OFFSET = 0
    COUNT = 0
    if os.path.exists(params_path):
        os.remove(params_path)
    get_params()
    ACCOUNT_NAME = get_account_name(GLOBAL_PARAMS)
    print(f"Start scraping {ACCOUNT_NAME}")

def check_existing(article_detail: ArticleData):
    global DF_ARTICLE
    return ((DF_ARTICLE['title'] == article_detail.title) & (DF_ARTICLE['content'] == article_detail.content)).any()

def get_links(tor = True):
    global CONTINUE_FLAG
    global GLOBAL_PARAMS
    url = f"https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&f=json&COUNT=10&is_ok=1&__biz={GLOBAL_PARAMS.biz}&key={GLOBAL_PARAMS.key}&uin={GLOBAL_PARAMS.uin}&pass_ticket={GLOBAL_PARAMS.pass_ticket}&OFFSET={OFFSET}"
    session = get_tor_session(tor)
    msg_json = session.get(url, headers=user_head(GLOBAL_PARAMS), verify=False).json()
    if (('can_msg_continue' in msg_json) and msg_json['can_msg_continue'] != 1):
        CONTINUE_FLAG = 0
    if "general_msg_list" in msg_json.keys():
        url_list = json.loads(msg_json['general_msg_list'])['list']
        return url_list
    return []

def parse_entry(article_detail: ArticleData, entry, tor = True):
    global OFFSET
    global COUNT
    global VERBOSE
    if 'app_msg_ext_info' in entry:
        entry = entry['app_msg_ext_info']
        flag = get_article(article_detail, entry, tor)
        if flag == "LinkError":
            print(f"Link Error: {entry}")
        if flag == "Scraped":
            if VERBOSE:
                print("Some articles have been scraped")
        COUNT += 1
        if "multi_app_msg_item_list" in entry:
            sublist = entry["multi_app_msg_item_list"]
            if VERBOSE:
                print('Sub-articles detected')
            for item in sublist:
                flag = get_article(article_detail, item, tor)
                if flag == "LinkError":
                    print(f"Link Error: {item}")
                COUNT += 1
        return flag
    else:
        print("No title")

def get_article(article_detail: ArticleData, entry, tor = True):
    global DF_ARTICLE
    flag = ""
    article_detail = ArticleData()
    if "title" in entry:
        article_detail.title = entry['title']
        article_detail.link = entry['content_url'].replace("amp;", "")
        article_detail.author = entry['author']
    else:
        return("LinkError")
    try:
        get_content(article_detail, tor)
    except Exception as e:
        print(f"Scrape Content Error. Title: {entry['title']}, link: {entry['content_url'].replace("amp;", "")}, error message: {e}")
    if check_existing(article_detail):
        flag = "Scraped"
    try:
        get_stats(article_detail, tor)
    except Exception as e:
        print(f"Scrape Stats Error. Title: {entry['title']}, link: {entry['content_url'].replace("amp;", "")}, error message: {e}")
    DF_ARTICLE = pd.concat([DF_ARTICLE, pd.DataFrame([vars(article_detail)])], ignore_index=True)
    time.sleep(random.uniform(2,5))
    return flag
    
def get_content(article_detail: ArticleData, tor = True):
    global PASSWORD
    session = get_tor_session(tor, PASSWORD)
    response = session.get(article_detail.link, headers=general_head, verify=False, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')

    # get article content
    article_text = soup.find(id="js_content") or soup.find(id="page_content") or soup.find(id="page-content")
    if article_text is None:
        if VERBOSE:
            print("Reloading content page...")
        session = get_tor_session(tor)
        response = session.get(article_detail.link, headers=general_head, verify=False, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_text = soup.find(id="js_content") or soup.find(id="page_content") or soup.find(id="page-content")

    if article_text:
        article_text = article_text.get_text()
        content = ''.join([text.strip() for text in article_text if text.strip()])
        article_detail.content = content
    else:
        print("No element was found.")
    
    # get article published date
    create_time = ''
    match = DATE_TIME_PATTERN.search(response.text)
    if match:
        timestamp = int(match.group(1))
        # Convert the timestamp to a datetime object
        create_time = datetime.datetime.fromtimestamp(timestamp)
    article_detail.pub_time = create_time

def get_stats(article_detail: ArticleData, tor = True):
    global GLOBAL_PARAMS
    global PASSWORD
    session = get_tor_session(tor, PASSWORD)
    read_num, like_num = 0, 0
    query_params = parse_qs(urlparse(article_detail.link).query)
    mid = query_params['mid'][0]
    sn = query_params['sn'][0]
    idx = query_params['idx'][0]
    detailUrl = f"https://mp.weixin.qq.com/mp/getappmsgext?f=json&mock=&fasttmplajax=1&uin={GLOBAL_PARAMS.uin}&key={GLOBAL_PARAMS.key}&pass_ticket={GLOBAL_PARAMS.pass_ticket}"
    response = session.post(detailUrl, headers=user_head(GLOBAL_PARAMS),
                            data=article_data(GLOBAL_PARAMS, mid, sn, idx), verify=False).json()
    if "appmsgstat" in response:
        info = response['appmsgstat']
        read_num = info['read_num']
        article_detail.read = read_num
        like_num = info['old_like_num']
        article_detail.like = like_num
    else:
        if VERBOSE:
            print("Reloading parameters, please wait...")
        get_params(reload = True)
        detailUrl = f"https://mp.weixin.qq.com/mp/getappmsgext?f=json&mock=&fasttmplajax=1&uin={GLOBAL_PARAMS.uin}&key={GLOBAL_PARAMS.key}&pass_ticket={GLOBAL_PARAMS.pass_ticket}"
        response = session.post(detailUrl, headers=user_head(GLOBAL_PARAMS),
                                data=article_data(GLOBAL_PARAMS, mid, sn, idx), verify=False).json()
        if "appmsgstat" in response:
            info = response['appmsgstat']
            read_num = info['read_num']
            article_detail.read = read_num
            like_num = info['old_like_num']
            article_detail.like = like_num

    article_detail.scrape_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def run(tor = True, day_max = 2500):
    global GLOBAL_PARAMS
    global OFFSET
    global COUNT
    global DF_ARTICLE
    global CONTINUE_FLAG
    global ACCOUNT_NAME
    start_time = time.time()
    initialize()
    
    start_count = load_log()
    offset_plus = load_offset(ACCOUNT_NAME)
    
    if os.path.exists(f"data/{ACCOUNT_NAME}.csv"):
        DF_ARTICLE = pd.read_csv(f"data/{ACCOUNT_NAME}.csv", index_col=None)
    else:
        DF_ARTICLE = pd.DataFrame(columns = ["author", "title", "content", "link", "read", "like", "pub_time", "scrape_time"])
    
    while True:
        url_list = get_links(tor)
        # First error detection: automatic refresh
        if len(url_list) == 0:
            print("Reloading parameters, please wait...")
            get_params(reload = True)
            url_list = get_links(tor)
            # Second error detection: break
            if len(url_list) == 0:
                print("Parameter error, verify account status")
                print(f"Article collection ended. {COUNT} articles collected.")
                sys.exit()
        first_overlap = True
        for entry in url_list:
            article_detail = ArticleData()
            flag = ""
            try:
                flag = parse_entry(article_detail, entry, tor)
            except Exception as e:
                print(e)
                print(f"Scrape Error: {entry}")
            if flag == "Scraped":
                if first_overlap:
                    first_overlap = False
                else:
                    OFFSET = OFFSET + offset_plus - 1
                    if offset_plus > 2:
                        offset_plus = 2
                        break
                    else: 
                        continue
            OFFSET += 1
            DF_ARTICLE.to_csv(f"data/{ACCOUNT_NAME}.csv", index=False)
            save_offset(ACCOUNT_NAME, OFFSET)
            save_log(start_count + COUNT)
        if start_count + COUNT > day_max:
            print(f"Daily maximum reached. {COUNT} articles collected.")
            sys.exit()
        if (CONTINUE_FLAG == 0):
            print(f"Article collection completed. {COUNT} articles collected.")
            sys.exit()
        print(f"Time elapsed: {(time.time() - start_time):.2f} seconds, {COUNT} articles scraped")

        time.sleep(random.uniform(2, 5))

def wechat_scraper(verbose = False, daymax = 2500):
    global VERBOSE
    VERBOSE = verbose
    tor = input("Use Tor to avoid IP blocks (default is yes)? Y/n: ").upper()
    if (tor == 'N') or (tor == 'NO'):
        tor = False
    else:
        tor = True
    run(tor, daymax)

def main():
    parser = argparse.ArgumentParser(description="WeChat Scraper Command-Line Interface")

    # Define command-line arguments
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode.')
    parser.add_argument('--daymax', type=int, default=2500, help='Maximum number of days to scrape. Default is 2500.')

    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with parsed arguments
    wechat_scraper(verbose=args.verbose, daymax=args.daymax)

##################################################################
# Pipeline 
# 1. Set up mitmproxy to retrieve parameters in VirtualBox (retrieve_params.py)
# 2. Initialize (initialize()) and get parameters(get_params())
# 3. Start retrieving article links (get_links())
# 4. For each entry in the links list, retrieve article information (parse_entry()), data saved in the ArticleData class
# 5. After each iteration, save article data into csv file for maximum record retention

if __name__ == "__main__":
    wechat_scraper()
    