import random, requests, re, threading, time, secrets, os
from hashlib import md5
from time import time as T
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from queue import Queue
import logging
import signal
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Running control flag
running = True

def signal_handler(signum, frame):
    global running
    print(f"\n{Fore.YELLOW}[!] Stopping bot gracefully...{Style.RESET_ALL}")
    running = False

signal.signal(signal.SIGINT, signal_handler)

class CustomSession:
    def __init__(self, pool_connections=200, pool_maxsize=200, max_retries=3):
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retries
        )
        
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

class LikeBot:
    def __init__(self, video_id, num_threads=100):
        self.video_id = video_id
        self.num_threads = num_threads
        self.session_pool = Queue()
        self.success_count = 0
        self.error_count = 0
        self.lock = threading.Lock()
        
        # Initialize session pool
        for _ in range(50):
            self.session_pool.put(CustomSession())

    def get_session(self):
        return self.session_pool.get()

    def return_session(self, session):
        self.session_pool.put(session)

    def send_like(self):
        global running
        session = self.get_session()
        
        try:
            while running:
                try:
                    # Parameters for like request
                    params = {
                        'WebIdLastTime': '0',
                        'aid': '1988',
                        'app_language': 'vi-VN',
                        'app_name': 'tiktok_web',
                        'aweme_id': self.video_id,
                        'browser_language': 'vi',
                        'browser_name': 'Mozilla',
                        'browser_online': 'true',
                        'browser_platform': 'Win32',
                        'channel': 'tiktok_web',
                        'cookie_enabled': 'true',
                        'device_platform': 'web_pc',
                        'focus_state': 'true',
                        'from_page': 'video',
                        'history_len': '4',
                        'is_fullscreen': 'false',
                        'is_page_visible': 'true',
                        'os': 'windows',
                        'priority_region': 'VN',
                        'referer': '',
                        'region': 'VN',
                        'screen_height': '864',
                        'screen_width': '1536',
                        'type': '1',  # 1 for like, 0 for unlike
                        'tz_name': 'Asia/Saigon',
                        'webcast_language': 'vi-VN',
                    }

                    headers = {
                        'authority': 'www.tiktok.com',
                        'accept': '*/*',
                        'accept-language': 'vi,en-US;q=0.9,en;q=0.8',
                        'content-type': 'application/x-www-form-urlencoded',
                        'origin': 'https://www.tiktok.com',
                        'referer': f'https://www.tiktok.com/@user/video/{self.video_id}',
                        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
                    }

                    url = f'https://www.tiktok.com/api/commit/item/digg/'
                    
                    response = session.session.post(
                        url,
                        params=params,
                        headers=headers,
                        timeout=5
                    )

                    if response.status_code == 200:
                        with self.lock:
                            self.success_count += 1
                            if self.success_count % 10 == 0:
                                print(f"{Fore.GREEN}[✓] LIKES SENT: {Style.BRIGHT}{self.success_count}{Style.RESET_ALL}", end='\r')

                    time.sleep(random.uniform(0.1, 0.3))  # Delay between requests

                except Exception as e:
                    with self.lock:
                        self.error_count += 1
                    time.sleep(1)

        finally:
            self.return_session(session)

    def start(self):
        print(f"\n{Fore.CYAN}[+] Starting TikTok Like Bot{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[+] Target Video ID: {self.video_id}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[+] Threads: {self.num_threads}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Press Ctrl+C to stop{Style.RESET_ALL}\n")

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(self.send_like) for _ in range(self.num_threads)]
            try:
                for future in futures:
                    future.result()
            except KeyboardInterrupt:
                pass

def main():
    os.system("cls" if os.name=="nt" else "clear")
    print(f"{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════╗")
    print(f"║        TikTok Like Bot v1.0        ║")
    print(f"╚════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    link = input(f"{Fore.YELLOW}[?] Enter TikTok Video URL: {Style.RESET_ALL}")
    
    try:
        page = requests.get(
            link,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/139.0.0.0'},
            timeout=10
        ).text
        video_id = re.search(r'\"video\":\{\"id\":\"(\d+)\"', page).group(1)
        print(f"\n{Fore.GREEN}[✓] Video ID: {video_id}{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[×] Error getting Video ID: {e}{Style.RESET_ALL}")
        return

    bot = LikeBot(video_id, num_threads=100)
    bot.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Bot stopped by user{Style.RESET_ALL}")