import json
import os
from playwright.sync_api import sync_playwright
import time


def download_file(page, save_dir):
    with page.expect_download() as download_info:
        page.click('div#downLoadFile')
    download = download_info.value

    suggested_filename = download.suggested_filename
    file_path = os.path.join(save_dir, suggested_filename)

    counter = 1
    while os.path.exists(file_path):
        name, ext = os.path.splitext(suggested_filename)
        file_path = os.path.join(save_dir, f"{name}_{counter}{ext}")
        counter += 1

    download.save_as(file_path)
    return file_path


def process_entries(data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        for entry in data:
            title = entry['title']
            url = entry['detailUrl']
            city = entry['city']

            print(f"Processing: {title}")
            page.goto(url)

            page.wait_for_selector('div#downLoadFile', state='visible')

            save_dir = os.path.join('downloads', city)
            os.makedirs(save_dir, exist_ok=True)

            try:
                file_path = download_file(page, save_dir)
                print(f"Downloaded: {file_path}")

                # 将文件路径添加到 entry 中
                entry['local_file_path'] = file_path
            except Exception as e:
                print(f"Error downloading {title}: {str(e)}")
                entry['local_file_path'] = None

            time.sleep(2)

        browser.close()

    return data


if __name__ == '__main__':
    # 读取 JSON 文件
    with open('all_search_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 处理数据并获取更新后的数据
    updated_data = process_entries(data)

    # 将更新后的数据写回 JSON 文件
    with open('all_search_results.json', 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    print("Updated all_search_results.json with local file paths.")