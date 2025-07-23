#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dood.py  —  解析 Dood /d/ 页面并下载
"""
import argparse, os, sys, requests, urllib.parse, subprocess
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # ❶ 关闭告警

def resolve(url: str) -> str:
    r = requests.get(url, timeout=15, verify=False)                 # ❷ verify=False
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    first = soup.select_one("div.download-content a[href]")
    if not first:
        raise RuntimeError("未找到第一层链接")
    inter = urllib.parse.urljoin(url, first["href"])
    r2 = requests.get(inter, timeout=15, verify=False)
    r2.raise_for_status()
    soup2 = BeautifulSoup(r2.text, "html.parser")
    final = soup2.select_one("div.download-generated a[href]")
    if not final:
        raise RuntimeError("未找到最终直链")
    return final["href"]

def ytdlp(u, out_dir):
    subprocess.run([
        "yt-dlp", "-o", os.path.join(out_dir, "%(title)s.%(ext)s"), u
    ], check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+"); ap.add_argument("-o", "--output", default="downloads")
    a = ap.parse_args(); os.makedirs(a.output, exist_ok=True)
    for u in a.urls:
        try:
            ytdlp(resolve(u), a.output)
        except Exception as e:
            print("✗", u, e, file=sys.stderr)

if __name__ == "__main__":
    main()
