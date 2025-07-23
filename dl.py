#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dl.py —— 一键下载视频

用法：
    python dl.py URL [URL ...] [-o OUTPUT_DIR] [--quality 1080]
"""
import argparse, os, re, subprocess, sys, urllib.parse
from bs4 import BeautifulSoup
import cloudscraper

def _layer2_src(layer1_url, scraper):
    vid = re.search(r"video=([^&]+)", layer1_url).group(1)
    resp = scraper.post(layer1_url, data={"video": vid, "play": ""},
                        headers={"Referer": layer1_url}); resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    iframe = soup.select_one("iframe");  assert iframe, "第二层 iframe 缺失"
    return iframe["src"]

def resolve_final(page_url, scraper):
    resp = scraper.get(page_url); resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    iframe1 = soup.select_one("iframe[src*='video=']"); assert iframe1, "未找到视频 iframe"
    return _layer2_src(urllib.parse.urljoin(page_url, iframe1["src"]), scraper)

def ytdlp(url, out_dir, h):
    cmd = ["yt-dlp", "--no-part", "--restrict-filenames",
           "-f", f"bestvideo[height<=?{h}]+bestaudio/best[height<=?{h}]",
           "-o", os.path.join(out_dir, "%(title)s.%(ext)s"), url]
    print("▶", " ".join(cmd)); subprocess.run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser(description="PornHoarder Downloader")
    ap.add_argument("urls", nargs="+"); ap.add_argument("-o", "--output", default="downloads")
    ap.add_argument("--quality", type=int, default=1080)
    a = ap.parse_args(); os.makedirs(a.output, exist_ok=True)
    scraper = cloudscraper.create_scraper()
    for u in a.urls:
        try: ytdlp(resolve_final(u, scraper), a.output, a.quality)
        except Exception as e: print("✗", u, e, file=sys.stderr)

if __name__ == "__main__": main()
