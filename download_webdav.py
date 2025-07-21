# download_webdav.py

import os, sys, urllib3
from webdav3.client import Client

# 1. Suppress HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. Read WebDAV configuration from environment
hostname = os.environ['WEBDAV_HOSTNAME']
username = os.environ['WEBDAV_USERNAME']
password = os.environ['WEBDAV_PASSWORD']
# Optional root path on server (e.g., '/remote.php/webdav')
root = os.environ.get('WEBDAV_ROOT', '').rstrip('/')

opts = {
    'webdav_hostname': hostname,
    'webdav_login':    username,
    'webdav_password': password
}
client = Client(opts)
client.verify = False  # Disable cert verification if self-signed


def safe_list(path: str):
    """
    Try to list a remote directory using several candidate paths.
    Returns the first non-empty list of items.
    """
    # Build full remote prefix
    p = path.strip('/')
    if root:
        base = root.lstrip('/')  # no leading slash for client
        full = f"{base}/{p}" if p else base
    else:
        full = p

    # Generate variants
    variants = []
    if full == '':
        variants = ['', '/']
    else:
        variants = [full, full+'/', '/'+full, '/'+full+'/']

    for cand in variants:
        try:
            items = client.list(cand)
            if items:
                print(f"[INFO] 列表成功: '{cand}' → {len(items)} items")
                return items
        except Exception:
            pass
    print(f"[WARN] 列出目录失败: 输入 '{path}', 尝试 {variants}")
    return []


def download_dir(path: str, local_path: str):
    # List items in remote path
    items = safe_list(path)
    if not items:
        print(f"[ERROR] 远程目录 '{path}' 不可访问，跳过下载")
        return

    # Ensure local directory
    os.makedirs(local_path, exist_ok=True)

    for entry in items:
        if entry in ('.', '..'):
            continue
        is_dir = entry.endswith('/')
        name = entry.rstrip('/')
        # Build remote sub-path
        sub_remote = f"{path.strip('/')}/{name}" if path.strip('/') else name
        sub_local = os.path.join(local_path, name)

        if is_dir:
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

    # Debug: list root items
    print("=== WebDAV 根目录列表 ===")
    for e in safe_list(''):
        print(" ", e)
    print("========================")

    download_dir(src, 'src')
