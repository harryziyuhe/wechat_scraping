import json
from utils import UserData
from urllib.parse import urlparse, parse_qs

class Requests:

    def request(self, flow):
        target = "getappmsgext"
        if target in flow.request.url:
            
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

            with open("params.json", mode="w", encoding="utf-8") as f:
                f.write(json.dumps(user.toJson(), indent = 4))

addons = [
    Requests()
]