from mitmproxy import http, ctx

class Requests:
    def load(self, loader):
        ctx.options.http2 = False
    
    def request(self, flow: http.HTTPFlow) -> None:
        target = {"weixin", "__biz=", "key="}
        if all(req in flow.request.url for req in target):
            f = open("C:\\Users\\vboxuser\\Documents\\key.txt", "w")
            url = flow.request.url
            try:
                f.write(url)
            except:
                f.write("error")
            f.close()

if __name__=="__main__":

    addons = [Requests()]