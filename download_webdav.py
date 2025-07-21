# download_webdav.py

import os, sys, urllib3
from webdav3.client import Client

# Suppress HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read WebDAV config from environment
opts = {
    'webdav_hostname': os.environ['WEBDAV_HOSTNAME'],
    'webdav_login':    os.environ['WEBDAV_USERNAME'],
    'webdav_password': os.environ['WEBDAV_PASSWORD'],
    'webdav_root':     os.environ.get('WEBDAV_ROOT', '/')
}

client = Client(opts)
client.verify = False  # disable cert verification if self-signed


def safe_list(path: str):
    """Try listing a path with or without trailing slash."""
    p = path.strip('/')
    for candidate in (p, p + '/'):
        try:
            return client.list(candidate)
        except Exception:
            continue
    print(f"[WARN] 列出目录失败: {path!r}")
    return []


def download_dir(remote_path: str, local_path: str):
    # Normalize remote_path
    r = remote_path.strip('/')
    print(f"\n👉 Downloading remote '{r or '/'}' to local '{local_path}/'\n")
    os.makedirs(local_path, exist_ok=True)

    items = safe_list(r)
    if r and not items:
        print(f"[ERROR] 远程目录 '{r}' 不存在或不可访问，跳过。\n")
        return

    for entry in items:
        name = entry.rstrip('/')
        sub_remote = f"{r}/{name}" if r else name
        sub_local = os.path.join(local_path, name)
        # Detect directory by trailing slash in entry
        if entry.endswith('/'):
            download_dir(sub_remote, sub_local)
        else:
            try:
                client.download(sub_remote, sub_local)
                print(f"  ✔ 下载文件: {sub_remote} → {sub_local}")
            except Exception as e:
                print(f"  [WARN] 下载失败 {sub_remote}: {e}")


if __name__ == '__main__':
    src = os.environ.get('INPUT_SRC_PATH') or (sys.argv[1] if len(sys.argv) > 1 else '')
    if not src:
        print("Usage: python download_webdav.py <remote_path>")
        sys.exit(1)

    # Debug root listing
    print("=== WebDAV 根目录列表 ===")
    for e in safe_list(''):
        print(" ", e)
    print("========================")

    download_dir(src, 'src')
