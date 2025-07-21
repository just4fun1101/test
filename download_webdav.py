# download_webdav.py
from webdav3.client import Client
import os

# 从环境变量读取（Actions 会替换）
opts = {
    'webdav_hostname': os.environ['WEBDAV_HOSTNAME'],
    'webdav_login':    os.environ['WEBDAV_USERNAME'],
    'webdav_password': os.environ['WEBDAV_PASSWORD']
}

client = Client(opts)
client.verify = False  # 如果你的服务器证书自签

def download_dir(remote_path, local_path):
    os.makedirs(local_path, exist_ok=True)
    for name in client.list(remote_path):
        if name in ('.', '..'):
            continue
        rpath = remote_path.rstrip('/') + '/' + name
        lpath = os.path.join(local_path, name)
        # 判断是目录还是文件
        if client.check(rpath):
            download_dir(rpath, lpath)
        else:
            client.download(rpath, lpath)
            print(f"Downloaded: {rpath} → {lpath}")

if __name__ == '__main__':
    # 从 workflow_dispatch 的输入里取 src_path
    import sys
    src = os.environ.get('INPUT_SRC_PATH') or sys.argv[1]
    download_dir(src, './src')
