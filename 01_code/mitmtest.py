class Requests:

    def request(self, flow):
        #print(flow.request.url)
        target = "getappmsgext"
        #with open("/Users/ziyuhe/Documents/debuglog.txt", "a") as k:
            #k.write(flow.request.url + "\n")
        if target in flow.request.url:
            f = open("/Users/ziyuhe/Documents/GitHub/wechat_scraping/01_code/key.txt", "w")
            url = flow.request.url
            try:
                f.write(url)
            except:
                f.write("error")
            f.close()
            cookie = ""
            for item in flow.request.cookies.fields:
                key = item[0]
                value = item[1]
                cookie += key + "=" + value + ";"
            f = open("/Users/ziyuhe/Documents/GitHub/wechat_scraping/01_code/cookie.txt", "w")
            try:
                f.write(cookie)
            except:
                f.write("error")
            f.close()

addons = [Requests()]