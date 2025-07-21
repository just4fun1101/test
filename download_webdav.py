# download_webdav.py

import os
import sys
import urllib3
from webdav3.client import Client

# 1. 抑制 HTTPS 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. 从环境变量读取 WebDAV 配置
opts = {
    'webdav_hostname': os.environ['WEBDAV_HOSTNAME'],
    'webdav_login':    os.environ['WEBDAV_USERNAME'],
    'webdav_password': os.environ['WEBDAV_PASSWORD']
}

client = Client(opts)
client.verify = False  # 如果服务器证书自签

def safe_list(path: str):
    """尝试列出目录，出错则返回空列表并打印错误。"""
    try:
        return client.list(path)
    except Exception as e:
        print(f"[WARN] 列出 {path!r} 时出错：{e}")
        return []

def download_dir(remote_path: str, local_path: str):
    # 规范化路径：去除首尾多余斜杠
    rp = remote_path.strip('/')
    lp = local_path.rstrip('/')

    print(f"\n👉 尝试下载远程目录: '{rp}' 到 本地: '{lp}/'\n")

    # 确保本地目录存在
    os.makedirs(lp, exist_ok=True)

    # 列出当前目录项
    items = safe_list(rp)
    if not items:
        print(f"[ERROR] 远程目录 `{rp}` 似乎不存在或不可访问，下载终止。\n")
        return

    for name in items:
        if name in ('.', '..'):
            continue
        sub_remote = f"{rp}/{name}"
        sub_local  = os.path.join(lp, name)
        # 如果是目录（webdav3.check 只对目录返回 True）
        if client.check(sub_remote):
            download_dir(sub_remote, sub_local)
        else:
            try:
                client.download(sub_remote, sub_local)
                print(f"  ✔ 下载文件: {sub_remote} → {sub_local}")
            except Exception as e:
                print(f"  [WARN] 下载 {sub_remote} 失败：{e}")

if __name__ == '__main__':
    # 从 INPUT_SRC_PATH 或者命令行参数读取
    src = os.environ.get('INPUT_SRC_PATH') or (sys.argv[1] if len(sys.argv)>1 else '')
    if not src:
        print("请传入 src_path，例如：python download_webdav.py '3/'")
        sys.exit(1)

    # —— 调试用：先打印根目录
    print("=== WebDAV 根目录列表 ===")
    for entry in safe_list(''):
        print(" ", entry)
    print("========================\n")

    download_dir(src, './src')
