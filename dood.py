#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dood.py —— 把 https://d000d.com/d/xxxxx 页面解析成最终直链并下载

用法:
    python dood.py URL [URL ...] [-o DIR]
"""
import argparse, os, re, sys, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from subprocess import run, CalledProcessError

def resolve(url: str) -> str:
    """两步抓最终跳转直链"""
    r = requests.get(url, timeout=15); r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    link = soup.select_one("div.download-content a[href]")
    if not link:
        raise RuntimeError("未找到第一跳链接")
    inter = urljoin("https://d000d.com", link["href"])
    r2 = requests.get(inter, timeout=15); r2.raise_for_status()
    soup2 = BeautifulSoup(r2.text, "html.parser")
    final = soup2.select_one("div.download-generated a[href]")
    if not final:
        raise RuntimeError("未找到最终直链")
    return final["href"]

def ytdlp(dl_url: str, out_dir: str):
    cmd = ["yt-dlp", "-o", os.path.join(out_dir, "%(title)s.%(ext)s"), dl_url]
    print("▶", " ".join(cmd), flush=True)
    run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("-o", "--output", default="downloads")
    a = ap.parse_args(); os.makedirs(a.output, exist_ok=True)
    for u in a.urls:
        try:
            ytdlp(resolve(u), a.output)
        except (Exception, CalledProcessError) as e:
            print("✗", u, e, file=sys.stderr)

if __name__ == "__main__":
    main()
