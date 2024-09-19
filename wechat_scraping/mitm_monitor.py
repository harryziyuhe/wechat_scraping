# monitor_traffic.py
from mitmproxy import ctx
from threading import Timer
import time

# Define the strings to search for
wechat = "mp.weixin.com"
target = ["getappmsgext", "biz", "key", "pass_ticket"]

# Event to handle the monitoring state
wechat_detected = False
target_detected = False

def target_detect():
    """Waits for 10 seconds to check if target links appears after wechat general links."""
    global target_detected
    print("Waiting 10 seconds to check for target links...")
    time.sleep(10)
    if target_detected:
        print("Target detected. Proceed to scraping.")
    else:
        print("Target not detected. WeChat version error.")
    ctx.master.shutdown()

class Requests:
    def request(self, flow):

        global wechat_detected, target_detected

        # Check if wechat is in the request URL
        if wechat in flow.request.url and not wechat_detected:
            wechat_detected = True

            # Start the timer to check for target after 10 seconds
            Timer(0, target_detect).start()

        # Check if target is in the request URL
        if all(keyword in flow.request.url for keyword in target):
            target_detected = True


addons = [
    Requests()
]
