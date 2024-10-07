from wechat_scraping.virtualbox.param_retriever import setProxy, clearProxy
import subprocess, os

setProxy(f"127.0.0.1:8888")
mitm_monitor_path = os.path.join(os.path.dirname(__file__), 'mitm_activity_monitor.py')
try:
    mitmprocess = subprocess.Popen(['mitmdump', '-s', mitm_monitor_path, '-p', '8888', '-q'])
    mitmprocess.wait()
finally:
    clearProxy()
