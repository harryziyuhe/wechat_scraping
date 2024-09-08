import json
from urllib.parse import urlparse, parse_qs

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

class Requests:

    def request(self, flow):
        # The mitm code will fuction when if we set target = "getappmsgext", but during the scraping process 
        # the one time parameters will be overwritten because mitmproxy will detect other urls with "getappmsgext"
        # that do not include the parameters we need, so to avoid this confusion we can set target to a list
        # that includes other key parameter names as well.
        # target = "getappmsgext"
        target = ["getappmsgext", "biz", "key", "pass_ticket"]
        if all(keyword in flow.request.url for keyword in target):
            
            # read cookie
            cookie = ""
            for item in flow.request.cookies.fields:
                key = item[0]
                value = item[1]
                cookie += key + "=" + value + ";"
            
            # read parameters
            parsed_url = urlparse(flow.request.url)
            query_params = parse_qs(parsed_url.query)
            biz = ""
            uin = ""
            pass_ticket = ""
            key = ""
            try:
                biz = query_params['__biz'][0]
                uin = query_params['uin'][0]
                pass_ticket = query_params['pass_ticket'][0]
                key = query_params['key'][0]
            except Exception as e:
                print(e)
            user = UserData(biz, uin, key, pass_ticket, cookie)

            with open("Z:\\params.json", mode="w", encoding="utf-8") as f:
                f.write(json.dumps(user.toJson(), indent = 4))

addons = [
    Requests()
]