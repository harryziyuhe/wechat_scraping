import time
import requests
from stem import Signal
from stem.control import Controller

def test_tor_password(password: str):
    try:
        # Connect to the Tor control port
        with Controller.from_port(port=9051) as controller:
            # Authenticate using the provided password
            controller.authenticate(password=password)
            print("Authentication successful!")

            # Send NEWNYM signal to renew the connection and change IP
            controller.signal(Signal.NEWNYM)
            print("Successfully sent NEWNYM signal to change IP.")

            # Wait a few seconds to allow the circuit to be rebuilt
            time.sleep(10)

            # Check if the new circuit is available for use
            # We test this by checking the IP address before and after NEWNYM
            current_ip = get_current_ip()
            print(f"Current IP: {current_ip}")

            # Send NEWNYM signal again to check the change
            controller.signal(Signal.NEWNYM)
            time.sleep(10)  # wait to ensure circuit change

            new_ip = get_current_ip()
            print(f"New IP: {new_ip}")

            if current_ip != new_ip:
                print("IP address renewed successfully.")
            else:
                print("IP address did not change. Try waiting longer between requests or adjusting your Tor settings.")

    except Exception as e:
        print(f"An error occurred: {e}")

def get_current_ip():
    # Function to get the current IP address via Tor
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    try:
        response = requests.get('http://httpbin.org/ip', proxies=proxies)
        return response.json().get('origin')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IP: {e}")
        return None

if __name__ == "__main__":
    password = input("Please input your torrc password: ")
    test_tor_password(password)
