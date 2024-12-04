import json
from playwright.sync_api import sync_playwright

def fetch_damai_forum(playwright):
    browser = playwright.chromium.launch(headless=False)
    data_list = []
    page = browser.new_page()
    page.goto('https://search.damai.cn/search.htm?spm=a2oeg.home.category.ditem_0.749223e1CQ8tBp&ctl=%E6%BC%94%E5%94%B1%E4%BC%9A&order=1&cty=%E5%8C%97%E4%BA%AC', timeout=60000)  # 增加超时时间到60秒
    page.wait_for_load_state('networkidle')

    while True:
        # 等待特定元素加载完成
        page.wait_for_selector('.items', timeout=60000)

        items = page.query_selector_all('.items')

        for item in items:
            # 获取活动名称
            event_name_element = item.query_selector('.items__txt__title a')
            event_name = event_name_element.inner_text() if event_name_element else 'N/A'

            # 获取艺人名称
            artist_element = item.query_selector('.items__txt__time')
            artist = artist_element.inner_text() if artist_element else 'N/A'

            location_element = item.query_selector('.items__txt__venue__icon')
            location = location_element.evaluate('node => node.nextSibling.textContent.trim()') if location_element else 'N/A'

            # 获取日期
            date_element = item.query_selector('.items__txt__time__icon')
            date = date_element.evaluate('node => node.nextSibling.textContent.trim()') if date_element else 'N/A'

            # 获取价格
            price_element = item.query_selector('.items__txt__price span')
            price = price_element.inner_text() if price_element else 'N/A'

            # 获取图片 URL
            img_element = item.query_selector('.items__img img')
            img_url = img_element.get_attribute('src') if img_element else 'N/A'

            # 获取详情 URL
            detail_element = item.query_selector('.items__img a')
            detail_url = detail_element.get_attribute('href') if detail_element else 'N/A'
            detail_url = f"https:{detail_url}" if detail_url.startswith("//") else detail_url

            # 打印提取的信息
            print(f"Event Name: {event_name}")
            print(f"Artist: {artist}")
            print(f"Location: {location}")
            print(f"Date: {date}")
            print(f"Price: {price}")
            print(f"Image URL: {img_url}")
            print(f"Detail URL: {detail_url}")
            print('-' * 40)

            # 将数据添加到列表
            data_list.append({
                "event_name": event_name,
                "artist": artist,
                "location": location,
                "date": date,
                "price": price,
                "image_url": img_url,
                "detail_url": detail_url
            })

        # 检查是否存在下一页按钮
        next_button = page.query_selector('li.number.active + li.number')
        if next_button:
            next_button.click()
            page.wait_for_load_state('networkidle')
        else:
            break

    browser.close()
    return data_list

def save_data_to_json(data_list, filename='damai.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    with sync_playwright() as playwright:
        data_list = fetch_damai_forum(playwright)
        save_data_to_json(data_list)