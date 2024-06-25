class Requests:

    def request(self, flow):
        #print(flow.request.url)
        target = {"weixin", "__biz=", "key=", "uin="}
        #with open("/Users/ziyuhe/Documents/debuglog.txt", "a") as k:
            #k.write(flow.request.url + "\n")
        if all(req in flow.request.url for req in target):
            print(flow.request.url)
            f = open("Z:\\key.txt", "w")
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
            f = open("Z:\\cookie.txt", "w")
            try:
                f.write(cookie)
            except:
                f.write("error")
            f.close()

addons = [Requests()]