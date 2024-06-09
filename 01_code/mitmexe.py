class Requests:

    def request(self, flow):
        target = {"weixin", "__biz=", "key="}
        #with open("/Users/ziyuhe/Documents/debuglog.txt", "a") as k:
            #k.write(flow.request.url + "\n")
        if all(req in flow.request.url for req in target):
            #print(flow.request.url)
            f = open("C:\\Users\\vboxuser\\Documents\\key.txt", "w")
            url = flow.request.url
            try:
                f.write(url)
            except:
                f.write("error")
            f.close()

addons = [Requests()]