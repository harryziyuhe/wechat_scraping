from mitmproxy import http, ctx
from notifypy import Notify


class Requests:
    def load(self, loader):
        ctx.options.http2 = False
    
    def request(self, flow: http.HTTPFlow) -> None:
        notification = Notify()
        notification.title = "Found"
        notification.message = "Found it"
        target = {"weixin", "__biz=", "key="}
        if all(req in flow.request.url for req in target):
            notification.send()
            f = open("Z:\key.txt", "w")
            url = flow.request.url
            try:
                f.write(url)
            except:
                f.write("error")
            f.close()

if __name__=="__main__":

    addons = [Requests()]