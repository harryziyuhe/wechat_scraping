from retrieve_params import setProxy, clearProxy
import subprocess

setProxy(f"127.0.0.1:8888")
try:
    mitmprocess = subprocess.Popen(['mitmdump', '-s', 'Z:/mitm_monitor.py', '-p', '8888', '-q'])
    mitmprocess.wait()
finally:
    clearProxy()
