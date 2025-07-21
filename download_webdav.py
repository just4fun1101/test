import os
import sys
import urllib3
from webdav3.client import Client

# 抑制 HTTPS 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 从环境变量读取 WebDAV 配置
opts = {
    'webdav_hostname': os.environ['WEBDAV_HOSTNAME'],
    'webdav_login':    os.environ['WEBDAV_USERNAME'],
    'webdav_password': os.environ['WEBDAV_PASSWORD']
}

client = Client(opts)
client.verify = False  # 如果服务器证书自签

def safe_list(path: str):
    try:
        return client.list(path)
    except Exception as e:
        print(f"[WARN] 列出 {path!r} 时出错：{e}")
        return []


def download_dir(remote_path: str, local_path: str):
    # 规范化 remote_path，允许 '3' 或 '3/'，并转换为带尾斜杠的形式
    rp = remote_path.lstrip('/')
    if rp and not rp.endswith('/'):
        rp = rp + '/'

    print(f"\n👉 尝试下载远程目录: '{rp or '/'}' 到 本地目录: '{local_path}/'\n")
    os.makedirs(local_path, exist_ok=True)

    items = safe_list(rp)
    # 如果指定了路径但没有列出内容，则认为路径不存在
    if rp and not items:
        print(f"[ERROR] 远程目录 `{rp}` 似乎不存在或不可访问，下载终止。\n")
        return

    for name in items:
        if name in ('.', '..'):
            continue
        sub_remote = rp + name
        sub_local = os.path.join(local_path, name.rstrip('/'))
        # 根据列表中目录项末尾是否有 '/' 判断类型
        if name.endswith('/'):
            download_dir(sub_remote, sub_local)
        else:
            try:
                client.download(sub_remote, sub_local)
                print(f"  ✔ 下载文件: {sub_remote} → {sub_local}")
            except Exception as e:
                print(f"  [WARN] 下载 {sub_remote} 失败：{e}")


if __name__ == '__main__':
    src = os.environ.get('INPUT_SRC_PATH') or (sys.argv[1] if len(sys.argv) > 1 else '')
    if not src:
        print("请传入 src_path，例如：python download_webdav.py '3/'")
        sys.exit(1)

    # 打印根目录列表，便于调试
    print("=== WebDAV 根目录列表 ===")
    for entry in safe_list(''):
        print(" ", entry)
    print("========================")

    download_dir(src, './src')
