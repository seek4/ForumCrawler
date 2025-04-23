from playwright.sync_api import sync_playwright, TimeoutError
import time
import json

target_cities = ["北京", "深圳", "成都", "上海", "合肥", "武汉", "重庆", "广州", "苏州",
                 "东莞", "杭州", "西安", "天津", "宁波", "郑州", "柳州", "佛山", "长沙",
                 "金华", "无锡", "长春", "保定", "南京", "嘉兴", "惠州", "济南", "青岛",
                 "厦门", "芜湖", "十堰"]


def crawler_city_traffic_rules(city_name: str):
    with (sync_playwright() as playwright):
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://flk.npc.gov.cn/")

        # 等待页面加载
        page.wait_for_load_state("networkidle")

        # 在输入框中输入检索文本
        search_text = f"{city_name}道路交通"
        page.fill("#flfgTitle", search_text)
        print("Search text:", search_text)

        # 点击检索按钮
        page.wait_for_selector('li[onclick="confirmFilter()"]', state="visible")
        page.click('li[onclick="confirmFilter()"]')
        print("Clicked search button")

        # 等待搜索结果加载
        try:
            page.wait_for_selector("#flData tr", timeout=60000)  # 等待结果表格加载
            print("Search results loaded")
        except TimeoutError:
            print("Timeout waiting for search results to load")
            return

        # 提取搜索结果
        results = page.evaluate("""
            () => {
                const rows = Array.from(document.querySelectorAll('#flData tr'));
                return rows.map(row => {
                    const cells = row.querySelectorAll('td');
                    const detailLink = cells[1].querySelector('.l-wen').getAttribute('onclick');
                    const detailUrl = detailLink ? detailLink.match(/'(.+?)'/)[1] : null;
                    return {
                        index: cells[0].textContent.trim(),
                        title: cells[1].querySelector('.l-wen').textContent.trim(),
                        organization: cells[2].textContent.trim(),
                        type: cells[3].textContent.trim(),
                        status: cells[4].textContent.trim(),
                        date: cells[5].textContent.trim(),
                        detailUrl: detailUrl ? 'https://flk.npc.gov.cn' + detailUrl.replace(/^\./, '') : null
                    };
                });
            }
        """)

        print(f"Found {len(results)} results")
        filter_results = []
        for result in results:
            result['city'] = city_name
            status = result['status']
            if status == '有效' and city_name in result['title'] and '海上' not in result['title'] and '轨道' not in result['title'] and '水上' not in result['title']:
                filter_results.append(result)
        print(f"city{city_name} Found {len(filter_results)} results after filter")

        time.sleep(5)
        return filter_results


if __name__ == "__main__":
    all_results = []
    for city in target_cities:
        city_results = crawler_city_traffic_rules(city)
        if len(city_results) > 0:
            all_results.extend(city_results)
        else:
            print(f"No results found for city {city}")
    print(f"all_results size: {len(all_results)}")
    with open('all_search_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)