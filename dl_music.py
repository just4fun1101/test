#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

YTDLP_PATH = "yt-dlp"
DOWNLOAD_ROOT = Path("Downloads")

YTDLP_BASE_ARGS = [
    "-x",
    "--audio-format", "141",
    "--embed-metadata",
    "--embed-thumbnail",
    "--parse-metadata", "playlist_index:%(track_number)s",
    "-o", str(DOWNLOAD_ROOT / "%(playlist_title)s/%(playlist_index)02d - %(artist)s - %(title)s.%(ext)s"),
]

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 dl_music.py <URL> [cookies_file]")
        sys.exit(1)

    url = sys.argv[1]
    cookies_file = sys.argv[2] if len(sys.argv) >= 3 else None

    DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    cmd = [YTDLP_PATH] + YTDLP_BASE_ARGS
    if cookies_file:
        cmd += ["--cookies", cookies_file]
    cmd.append(url)

    print("Running:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"yt-dlp failed with exit code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
