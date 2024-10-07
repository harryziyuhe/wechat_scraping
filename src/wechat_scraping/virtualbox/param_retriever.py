import subprocess, platform, os, argparse

def setProxy(proxy_server):
    """
    Sets the system-wide browser level proxy settings based on the operating system.

    Args:
        proxy_server (str): The proxy server address and port, e.g. "127.0.0.1:8080" 
    """
    # Split the proxy server into IP and port componnets
    proxy_ip, proxy_port = proxy_server.split(":")

    # Detect the operating system
    os_type = platform.system()

    if os_type == "Darwin": # macOS configuration

        # Set the network service name; adjust if needed (e.g., Wi-Fi, Ethernet)
        network_service = "Ethernet"

        # Check if network service is valid
        check_cmd = f'networksetup -listallnetworkservices'
        output = subprocess.run(check_cmd.split(), capture_output = True, text = True)
        print("Available network service:")
        print(output.stdout)

        # Ensure the input network service name exists
        if network_service not in output.stdout:
            print(f"Error: The network service '{network_service}' is not valid.")
            return
        
        # Base commands to set proxy for HTTP and HTTPS
        cmd_base = f'networksetup -setwebproxy {network_service} {proxy_ip} {proxy_port}'
        cmd_base_secure = f'networksetup -setsecurewebproxy {network_service} {proxy_ip} {proxy_port}'

        # Enable proxy settings
        print("Enabling proxy...")
        subprocess.call(cmd_base.split())
        subprocess.call(cmd_base_secure.split())
        subprocess.call(f'networksetup -setwebproxystate {network_service} on'.split())
        subprocess.call(f'networksetup -setsecurewebproxystate {network_service} on'.split())
    
    elif os_type == "Linux":  # Linux configuration

        # Set the network service name; adjust if needed (e.g., Wi-Fi, Ethernet)
        network_connection = "Ethernet"

        # Check if network service is valid
        check_cmd = 'nmcli connection show'
        output = subprocess.run(check_cmd.split(), capture_output=True, text=True)
        print("Available network connections:")
        print(output.stdout)

        # Ensure the input network connection exists
        if network_connection not in output.stdout:
            print(f"Error: The network connection '{network_connection}' is not valid.")
            return

        # Base commands to set proxy for HTTP and HTTPS using nmcli
        cmd_http = f'nmcli connection modify "{network_connection}" proxy.http {proxy_ip}:{proxy_port}'
        cmd_https = f'nmcli connection modify "{network_connection}" proxy.https {proxy_ip}:{proxy_port}'

        # Enable proxy settings
        print("Enabling proxy...")
        subprocess.call(cmd_http.split())
        subprocess.call(cmd_https.split())
        subprocess.call(f'nmcli connection up "{network_connection}"'.split())

        # Set environment variables as an additional method
        print("Setting proxy environment variables...")
        env_vars = {
            "http_proxy": f"http://{proxy_ip}:{proxy_port}",
            "https_proxy": f"https://{proxy_ip}:{proxy_port}",
            "HTTP_PROXY": f"http://{proxy_ip}:{proxy_port}",
            "HTTPS_PROXY": f"https://{proxy_ip}:{proxy_port}"
        }

        for var, value in env_vars.items():
            set_env_cmd = f'export {var}={value}'
            subprocess.run(['bash', '-c', set_env_cmd])
            print(f"Set {var} to {value}")

    elif os_type == "Windows": # Windows configuration
        # Set the network service name; adjust if needed (e.g., Wi-Fi, Ethernet)
        network_service = "Ethernet"

        # Check if the network interface is valid
        check_cmd = 'netsh interface show interface'
        output = subprocess.run(check_cmd, capture_output = True, text = True)
        print("Available network interfaces:")
        print(output.stdout)

        # Ensure the input network service name exists
        if network_service not in output.stdout:
            print(f"Error: The network service '{network_service}' is not valid.")
            return
        
        # Enable system-wide proxy via registry modifications
        print("Enabling proxy...")
        cmd_open = 'reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyEnable /t REG_DWORD /d 1 /f'
        cmd_proxy = f'reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyServer /t REG_SZ /d "{proxy_ip}:{proxy_port}" /f'
        print(cmd_open)
        subprocess.call(cmd_open, shell=True)
        subprocess.call(cmd_proxy, shell=True)
        
    else:
        print("Unsupported operating system.")

def clearProxy():
    """
    Clears the proxy settings based on the operating system.
    """
    # Detect the operating system
    os_type = platform.system()

    if os_type == 'Darwin':  # macOS
        # Set the network service name, such as "Wi-Fi" or "Ethernet"
        network_service = 'Ethernet'

        # Check if the network service is valid
        check_cmd = 'networksetup -listallnetworkservices'
        output = subprocess.run(check_cmd.split(), capture_output=True, text=True)
        print("Available network services:")
        print(output.stdout)

        # Ensure the input network service name exists
        if network_service not in output.stdout:
            print(f"Error: The network service '{network_service}' is not valid.")
            return

        # Disable HTTP and HTTPS proxy settings
        subprocess.call(f'networksetup -setwebproxystate {network_service} off'.split())
        print("HTTP proxy disabled.")
        subprocess.call(f'networksetup -setsecurewebproxystate {network_service} off'.split())
        print("HTTPS proxy disabled.")

    elif os_type == 'Windows': # Windows
        # Set the network service name; adjust if needed (e.g., Wi-Fi, Ethernet)
        network_service = 'Ethernet' 

        # Check if the network interface is valid
        check_cmd = 'netsh interface show interface'
        output = subprocess.run(check_cmd, capture_output=True, text=True, shell=True)
        print("Available network interfaces:")
        print(output.stdout)

        # Ensure the input network interface name exists
        if network_service not in output.stdout:
            print(f"Error: The network service '{network_service}' is not valid.")
            return

        # Disable proxy settings via registry modification
        print("Disabling proxy on Windows...")
        cmd_close = 'reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyEnable /t REG_DWORD /d 0 /f'
        subprocess.call(cmd_close, shell=True)
        print("Proxy settings cleared.")

    else:
        print("Unsupported operating system.")


def proxyThread(port = '8888', quiet = False):
    """
    Starts the mitmproxy process with the process settings enabled.

    Args:
        port (str): The port on which mitmproxy will run.
        quiet (bool): Whether to run mitmproxy in quiet mode.
    """
    global mitmprocess

    # Set the proxy to redirect traffic to mitmproxy
    setProxy(f"127.0.0.1:{port}")

    mitmproxy_path = os.path.join(os.path.dirname(__file__), 'mitm_proxy_manager.py')

    # Start mitmproxy
    if quiet:
        mitmprocess = subprocess.Popen(['mitmdump', '-s', mitmproxy_path, '-p', port, '-q'])
    else:
        mitmprocess = subprocess.Popen(['mitmdump', '-s', mitmproxy_path, '-p', port])

def stopProxy():
    """
    Stops the mitmproxy process and clears settings.
    """
    if 'mitmprocess' in globals():
        mitmprocess.terminate()  # Terminate the mitmproxy process
        mitmprocess.wait()  # Wait for the process to finish
        print("mitmproxy terminated.")
    clearProxy()  # Clear proxy settings after stopping mitmproxy

def retrieve_params(quiet = False):
    try:
        proxyThread(port = '8888', quiet = quiet)
        mitmprocess.wait()
    except:
        stopProxy()

def main():
    parser = argparse.ArgumentParser(description="Run retrieve_params with optional quiet mode.")
    parser.add_argument('-q', '--quiet', action='store_true', help='Run in quiet mode.')
    
    args = parser.parse_args()
    
    retrieve_params(quiet=args.quiet)


if __name__ == "__main__":
    retrieve_params()