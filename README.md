# Scraping WeChat Official Accounts

## Setup
Besides installing necessary Python packages, the most important setup involves two steps:
1. Create two standalone environments, one for capturing web traffic and one for scraping.
2. Install a functional verion of WeChat in the web traffic monitoring environment (the pipeline does not work with the most updated version of WeChat on MacOS and Windows. Need to install an older version released before April, 2023.)

To check whether the current installed version of WeChat works, run `python wechat_version.py` in the web traffic monitoring environment.

## Pipeline
We use a two-step approach to scrape content and statistics from WeChat official account posts:

### 1. Mitmproxy for URL Interception
We use `mitmproxy` to detect and intercept URLs that contain key parameters necessary for mimicking GET and POST requests to the WeChat server. This involves manually operating the WeChat app or web interface to capture these requests.

### 2. Data Scraping Using Intercepted Parameters
Once we have the required parameters, we use them to programmatically retrieve a list of posts, along with the content and statistics (such as read and like counts) for each post.

To run the `mitmproxy` component, we need to modify the network proxies so that all internet traffic is routed through the port designated by `mitmproxy`. However, this setup can interfere with the scraping process, as the `requests` package may flag warnings when requests pass through the proxy port. Additionally, to implement this approach at scale and avoid IP blocking, we need to use Tor for anonymity.

To avoid potential proxy conflicts, we suggest running the `mitmproxy` code in a VirtualBox environment with an older version of WeChat (released prior to April 2023) installed. Setting the current folder as the shared folder will allow indirect communication between `mitmproxy` and the scraper, which is essential for the pipeline to function correctly.

## Additional Features and Future Plans

- **Automatic Proxy Configuration:** Proxies for both `mitmproxy` and Tor will be automatically set up. The password in the `torrc` file is `"secret"`.
- **Automatic Parameter Retrieval:** The `uin` and `biz` ID parameters will be automatically retrieved, eliminating the need for users to manually specify them.
- **Skip Previously Scraped Posts:** The scraper will automatically skip posts that have already been scraped and adjust the offset parameter accordingly.
- **Wi-Fi Connection Requirement:** Currently, users must use Wi-Fi connections. However, future editions of the tool will also support Ethernet connections.

## Running the Pipeline

1. **Set the Refresh Button Figure:** Before running the pipeline, take a screenshot of the refresh button on a WeChat official account post and save the image as `refresh.png` in the `fig` folder.
2. **Log in to WeChat:** In the VirtualBox machine, open WeChat and log in.
3. **Retrieve Parameters:**
    - In the VirtualBox machine, navigate to the `wechat_scraping` folder.
    - Run `python retrieve_params.py` in the terminal. 
    - You can choose to either display all requests that `mitmproxy` detects or use the quiet mode to suppress output.
4. **Run the Scraper:**
    - On the host machine, navigate to the `wechat_scraping` folder.
    - Run `python wechatcollect.py` in the terminal.
    - You can choose to either enable or disable Tor functionality.
5. **Start Scraping:**
    - Wait until "Detecting" appears in the terminal on the host machine.
    - Then, in the VirtualBox machine, click on any post belonging to the target official account on WeChat.
