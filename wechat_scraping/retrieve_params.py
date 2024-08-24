import subprocess

def setProxy(proxy_server, enable = True):
    #proxy_server input should include ip and port number, e.g. "192.168.1.1:8080" 
    proxy_ip, proxy_port = proxy_server.split(":")

    # set network service name, such as "Wi-Fi" or "Ethernet"
    network_service = "Wi-Fi"

    # check if network service is valid
    check_cmd = f'networksetup -listallnetworkservices'
    output = subprocess.run(check_cmd.split(), capture_output = True, text = True)
    print("Available network service:")
    print(output.stdout)

    if network_service not in output.stdout:
        print(f"Error: The network service '{network_service}' is not valid.")
        return
    
    cmd_base = f'networksetup -setwebproxy {network_service} {proxy_ip} {proxy_port}'
    cmd_base_secure = f'networksetup -setsecurewebproxy {network_service} {proxy_ip} {proxy_port}'

    if enable:
        # enable proxy
        print("Enabling proxy...")
        subprocess.call(cmd_base.split())
        subprocess.call(cmd_base_secure.split())
        subprocess.call(f'networksetup -setwebproxystate {network_service} on'.split())
        subprocess.call(f'networksetup -setsecurewebproxystate {network_service} on'.split())
    else:
        # disable proxy
        print("Disabling proxy...")
        subprocess.call(f'networksetup -setwebproxystate {network_service} off'.split())
        subprocess.call(f'networksetup -setsecurewebproxystate {network_service} off'.split())

def clearProxy():
	# 设定网络服务的名称，如 'Wi-Fi' 或 'Ethernet'
	network_service = 'Wi-Fi'

	# 检查网络服务是否有效
	check_cmd = f'networksetup -listallnetworkservices'
	output = subprocess.run(check_cmd.split(), capture_output=True, text=True)
	print("Available network services:")
	print(output.stdout)

	# 确保输入的网络服务名称存在
	if network_service not in output.stdout:
		print(f"Error: The network service '{network_service}' is not valid.")
		return

	# 禁用HTTP代理
	subprocess.call(f'networksetup -setwebproxystate {network_service} off'.split())
	print("HTTP proxy disabled.")

	# 禁用HTTPS代理
	subprocess.call(f'networksetup -setsecurewebproxystate {network_service} off'.split())
	print("HTTPS proxy disabled.")

def proxyThread(port = '8888', quiet = False):
    global mitmprocess

    setProxy(f"127.0.0.1:{port}")

    if quiet:
        mitmprocess = subprocess.Popen(['mitmdump', '-s', 'mitmproxy.py', '-p', port, '-q'])
    else:
        mitmprocess = subprocess.Popen(['mitmdump', '-s', 'mitmproxy.py', '-p', port])

def stopProxy():
    if 'mitmprocess' in globals():
        mitmprocess.terminate()  # Terminate the mitmproxy process
        mitmprocess.wait()  # Wait for the process to finish
        print("mitmproxy terminated.")
    clearProxy()  # Always clear proxy settings

if __name__ == "__main__":
    quiet = input("Do you want to run mitmproxy in quiet mode?Y/n: ").upper()
    if (quiet == "N") or (quiet == "No"):
        quiet = False
    else:
        quiet = True
    try:
        proxyThread(port = '8888', quiet = quiet)
        mitmprocess.wait()
    except:
        stopProxy()