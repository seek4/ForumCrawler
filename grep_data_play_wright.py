from playwright.sync_api import sync_playwright
import json
from urllib.parse import urlparse, parse_qs

from nga_post import NGAPost


def fetch_nga_forum(playwright, page_index):
    browser = playwright.chromium.launch(headless=True)
    data_list = []
    for i in range(1, page_index + 1):
        page = browser.new_page()
        page.goto(f'https://bbs.nga.cn/thread.php?fid=-343809&page={i}')
        page.wait_for_load_state('networkidle')

        threads = page.query_selector_all('tr[class*="topicrow"]')
        for thread in threads:
            title = thread.query_selector('a.topic').text_content().strip()
            url = thread.query_selector('a.topic').get_attribute('href')
            replies = thread.query_selector('a.replies').text_content().strip()
            post_time_element = thread.query_selector('span.postdate')
            post_time_title = post_time_element.get_attribute('title') if post_time_element else None
            content = "Content not fetched"  # Placeholder for content
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            post_id = query_params.get('tid', [None])[0]

            if url.startswith('http://') or url.startswith('https://'):
                content = fetch_nga_post_content(browser, url)
            else:
                print(f"Invalid URL skipped: {url}")

            data = NGAPost(post_id, title, content, url, replies, post_time_title)
            print(data.to_dict())
            data_list.append(data.to_dict())

    browser.close()
    return data_list


def fetch_nga_post_content(browser, post_url):
    page = browser.new_page()
    try:
        page.goto(post_url)
        page.wait_for_load_state('networkidle')
        content = page.query_selector('.postcontent')
        if content:
            print(content.text_content().strip())
            return content.text_content().strip()
    except Exception as e:
        print(f"Error fetching content from {post_url}: {str(e)}")
    return "Content not fetched"


def save_data_to_json(data_list, filename='nga_posts.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    with sync_playwright() as playwright:
        data_list = fetch_nga_forum(playwright, 10)  # Fetch data from the first 10 pages
        save_data_to_json(data_list)
