#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

# 配置选项
USER_NAME = "junqhao"
REPO_NAME = "echoplan-static-cdn"
BRANCH_OR_TAG = "latest"

BASE_PURGE_URL = f"https://purge.jsdelivr.net/gh/{USER_NAME}/{REPO_NAME}@{BRANCH_OR_TAG}"

def purge_single_file(cdn_subpath):
    # 统一转换斜杠格式
    clean_subpath = cdn_subpath.replace("\\", "/").strip("/")
    full_purge_url = f"{BASE_PURGE_URL}/{clean_subpath}"
    
    req = urllib.request.Request(full_purge_url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            data = json.loads(res_body)
            status = data.get("status", "unknown")
            print(f"✅ [{status}] {full_purge_url}")
    except urllib.error.HTTPError as e:
        print(f"❌ [HTTP {e.code}] {full_purge_url}")
    except Exception as e:
        print(f"❌ [Error] {full_purge_url} - {e}")

def main():
    if len(sys.argv) < 2:
        print("❌ 错误: 请指定路径！")
        print("使用示例: python3 purge_cdn.py /path/to/my_folder")
        print("         python3 purge_cdn.py /path/to/dissolve.webm")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.exists(input_path):
        print(f"❌ 错误: 本地找不到指定路径 '{input_path}'")
        sys.exit(1)

    # 提取输入的最后一级名称（文件夹名或文件名）
    # 例如 input_path 为 "/Users/xxx/videos/v"，base_name 就是 "v"
    # 例如 input_path 为 "v/dissolve.webm"，base_name 就是 "dissolve.webm"
    base_name = os.path.basename(os.path.normpath(input_path))

    print(f"🚀 开始刷新 jsDelivr 缓存")
    print(f"📌 CDN 前缀根目录映射: {BASE_PURGE_URL}/{base_name}")
    print("-" * 65)

    count = 0

    # 情况 1：如果传入的是单个文件
    if os.path.isfile(input_path):
        purge_single_file(base_name)
        count = 1

    # 情况 2：如果传入的是文件夹
    else:
        for root, dirs, files in os.walk(input_path):
            # 过滤隐藏文件夹
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            
            for file in files:
                if file.startswith("."):
                    continue  # 跳过隐藏文件
                
                # 计算文件相对于传入文件夹的子路径
                full_local_file_path = os.path.join(root, file)
                rel_to_input = os.path.relpath(full_local_file_path, input_path)
                
                # 拼接成 CDN 的子路径：最后一级文件夹名 + 内部相对路径
                if rel_to_input == ".":
                    cdn_subpath = base_name
                else:
                    cdn_subpath = os.path.join(base_name, rel_to_input)
                
                purge_single_file(cdn_subpath)
                count += 1

    print("-" * 65)
    print(f"🎉 刷新完成！共处理 {count} 个文件。")

if __name__ == "__main__":
    main()
