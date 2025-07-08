# 🛡️ InstaBrute - Ethical Multi-Threaded Brute Forcer

## 🚀 Overview

**InstaBrute** is a multi-threaded, proxy-rotating brute force tool built for ethical penetration testing and login security auditing. It allows the user to test a known username against a password wordlist and optionally route attempts through rotating HTTP/HTTPS proxies.

> ⚠️ This tool is for **educational** and **authorized security testing** only.

---

## 🔍 Features

- 🔁 Supports proxy rotation from a file (`IP:PORT`)
- 🔐 Custom login URL and POST body
- ⚡ Fast, multi-threaded password testing
- 📜 Wordlist support (e.g., `rockyou.txt`)
- 🔥 Auto-skip dead/failing proxies
- 🎯 Clean CLI argument interface

---

## ⚙️ Usage

```bash
python3 bruter.py \
  --url https://yourtarget.com/login \
  --username Target_user \
  --wordlist passwords.txt \
  --proxies proxy.txt \
