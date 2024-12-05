import json
import logging
from playwright.sync_api import sync_playwright, TimeoutError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_damai_forum(playwright):
    browser = playwright.chromium.launch(headless=False)
    data_list = []
    page = browser.new_page()
    page.goto(
        'https://search.damai.cn/search.htm?spm=a2oeg.home.category.ditem_0.749223e1CQ8tBp&ctl=%E6%BC%94%E5%94%B1%E4%BC%9A&order=1&cty=%E5%8C%97%E4%BA%AC',
        timeout=60000)  # 增加超时时间到60秒
    page.wait_for_load_state('networkidle')
    logging.info(page.content())
    target_cities = ['北京', '上海', '深圳']
    target_categories = ['音乐会', '曲苑杂坛', '演唱会', '话剧歌剧', '展览休闲', '舞蹈芭蕾', '体育', '儿童亲子']

    cities = page.query_selector_all('.factor-content-item')
    for city in cities:
        city_name = city.inner_text().strip()
        if city_name in target_cities:
            print(f"Scraping city: {city_name}")

            # 点击城市
            city.click()
            page.wait_for_load_state('networkidle')

            # 获取分类列表
            categories = page.query_selector_all('.factor-content-item')
            for category_index, category in enumerate(categories):
                category_name = category.inner_text().strip()
                if category_name not in target_categories:
                    continue
                print(f"Scraping category: {category_name}")
                # 点击分类
                category.click()
                page.wait_for_load_state('networkidle')

                page_count = 0
                while True:
                    try:
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
                            location = location.split('|')[-1].strip()  # 去掉前缀

                            # 获取日期
                            date_element = item.query_selector('.items__txt__time__icon')
                            date = date_element.evaluate('node => node.nextSibling.textContent.trim()') if date_element else 'N/A'

                            # 获取价格
                            price_element = item.query_selector('.items__txt__price span')
                            price = price_element.inner_text() if price_element else 'N/A'

                            # 获取售票状态
                            status_element = item.query_selector('.items__txt__price')
                            status = status_element.inner_text().split()[-1] if status_element else 'N/A'

                            # 获取图片 URL
                            img_element = item.query_selector('.items__img img')
                            img_url = img_element.get_attribute('src') if img_element else 'N/A'

                            # 获取详情 URL
                            detail_element = item.query_selector('.items__img')
                            detail_url = detail_element.get_attribute('href') if detail_element else 'N/A'
                            detail_url = f"https:{detail_url}" if detail_url.startswith("//") else detail_url

                            # 打印提取的信息
                            print(f"City: {city_name} category: {category_name}")
                            print(f"Event Name: {event_name}")
                            print(f"Artist: {artist}")
                            print(f"Location: {location}")
                            print(f"Date: {date}")
                            print(f"Price: {price}")
                            print(f"Status: {status}")
                            print(f"Image URL: {img_url}")
                            print(f"Detail URL: {detail_url}")
                            print('-' * 40)

                            # 将数据添加到列表
                            data_list.append({
                                "city": city_name,
                                "category": category_name,
                                "event_name": event_name,
                                "artist": artist,
                                "location": location,
                                "date": date,
                                "price": price,
                                "status": status,
                                "image_url": img_url,
                                "detail_url": detail_url
                            })

                        # 检查是否存在下一页按钮
                        next_button = page.query_selector('li.number.active + li.number')

                        print(f"************************next page {page_count}*********************************")
                        if next_button:
                            next_button.click()
                            page.wait_for_load_state('networkidle')
                            page_count = page_count + 1
                        else:
                            print("No more pages found, ending scraping.")
                            break
                    except TimeoutError:
                        print("Timeout while waiting for elements, continuing to next page.")
                        break
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        break
    print(f"all event count {len(data_list)} page count {page_count}")
    browser.close()
    return data_list

def save_data_to_json(data_list, filename='damai.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    with sync_playwright() as playwright:
        data_list = fetch_damai_forum(playwright)
        save_data_to_json(data_list)