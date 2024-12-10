import json
import logging
from playwright.sync_api import sync_playwright, TimeoutError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_damai_all(playwright):
    browser = playwright.chromium.launch(headless=False)
    data_list = []
    id_set = set()  # 用于存储已存在的id
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
                            location = location_element.evaluate(
                                'node => node.nextSibling.textContent.trim()') if location_element else 'N/A'
                            location_split = location.split('|')  # 去掉前缀
                            city_parse = location_split[0].strip()
                            location_str = location_split[1].strip()

                            # 获取日期
                            date_element = item.query_selector('.items__txt__time__icon')
                            date = date_element.evaluate(
                                'node => node.nextSibling.textContent.trim()') if date_element else 'N/A'

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

                            id = detail_url.split('id=')[1].split('&')[0] if 'id=' in detail_url else 'N/A'

                            # 检查id是否重复
                            if id in id_set:
                                logging.warning(f"Duplicate id found: {id}")
                                continue
                            id_set.add(id)

                            # 打印提取的信息
                            print(f"City: {city_name} category: {category_name}")
                            print(f"ID: {id}")
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
                                "id": id,
                                "city": city_parse,
                                "category": category_name,
                                "event_name": event_name,
                                "artist": artist,
                                "location": location_str,
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
    save_all_to_json(data_list)
    # for data in data_list:
    #     detail_url = data['detail_url']
    #     page.goto(detail_url)
    #     page.wait_for_load_state('networkidle')
    #
    #     # 获取经纬度信息
    #     map_element = page.query_selector('a[data-spm="daddress"]')
    #     if map_element:
    #         map_href = map_element.get_attribute('href')
    #         lng_lat = map_href.split('lng=')[1].split('&lat=')
    #         data['longitude'] = lng_lat[0]
    #         data['latitude'] = lng_lat[1].split('&')[0]
    #     else:
    #         data['longitude'] = 'N/A'
    #         data['latitude'] = 'N/A'
    #
    #     # 获取详情描述信息
    #     detail_description_element = page.query_selector('#detail .words')
    #     data['detail_description'] = detail_description_element.inner_html() if detail_description_element else 'N/A'
    #     print(f"detail：{data['detail_description']} lat,lng {data['longitude']} {data['latitude']}")
    #
    #     # 将数据写入文件
    #     save_data_to_json(data)

    print("finish crawler")
    browser.close()
    return data_list


def save_all_to_json(data_list, filename='damai_all.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

def save_data_to_json(data, filename='damai.json'):
    with open(filename, 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write('\n')  # 添加换行符，确保每条记录独占一行


import re

# 读取源文件


# 修复 JSON 格式的函数
def fix_json(json_str):
    # 在每个 "}\n{" 的位置插入逗号
    fixed_json = re.sub(r'}\s*{', '},\n{', json_str)
    return fixed_json

def fetch_detail(playwright):
    with open('damai_all.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)

    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    for data in data_list:
        detail_url = data['detail_url']
        page.goto(detail_url)
        page.wait_for_load_state('networkidle')

        # 获取经纬度信息
        map_element = page.query_selector('a[data-spm="daddress"]')
        if map_element:
            map_href = map_element.get_attribute('href')
            lng_lat = map_href.split('lng=')[1].split('&lat=')
            data['longitude'] = lng_lat[0]
            data['latitude'] = lng_lat[1].split('&')[0]
        else:
            data['longitude'] = 'N/A'
            data['latitude'] = 'N/A'

        # 获取详情描述信息
        detail_description_element = page.query_selector('#detail .words')
        data['detail_description'] = detail_description_element.inner_html() if detail_description_element else 'N/A'
        print(f"detail：{data['detail_description']} lat,lng {data['longitude']} {data['latitude']}")

        # 将数据写入文件
        save_data_to_json(data, 'damai_detail.json')

    print("finish fetching details")
    browser.close()



def fill_detail_with_data():
    with open('damai_all.json', 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    with open('damai_fixed.json','r',encoding='utf-8') as deatil_f:
        detail_list = json.load(deatil_f)
    for data in data_list:
        detail_url = data['detail_url']
        for detail_data in detail_list:
            if detail_data['detail_url'] == detail_url:
                data['longitude'] = detail_data['longitude']
                data['latitude'] = detail_data['latitude']
                data['detail_description'] = detail_data['detail_description']

    def save_all_to_json(data_list, filename='damai_all_detail.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)
    save_all_to_json(data_list)



if __name__ == '__main__':
    fill_detail_with_data()
    # with sync_playwright() as playwright:
    #     #fetch_damai_all(playwright)
    #     fetch_detail(playwright)
    # with open('damai.json', 'r', encoding='utf-8') as f:
    #     data = f.read()
    # # 修复后的数据
    # fixed_data = fix_json(data)
    #
    # # 将修复后的数据写入新文件
    # with open('damai_fixed.json', 'w', encoding='utf-8') as f:
    #     f.write(fixed_data)
    #
    # print("修复完成，结果已保存至 output.json 文件。")