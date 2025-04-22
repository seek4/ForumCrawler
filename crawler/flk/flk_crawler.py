from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=False)  # 设置headless=True可以在后台运行
    page = browser.new_page()
    page.goto("https://flk.npc.gov.cn/")

    # 等待页面加载
    page.wait_for_load_state("networkidle")

    # 在输入框中输入检索文本
    search_text = "广东安全交通法规"  # 替换成你想检索的实际文本
    page.fill("#flfgTitle", search_text)
    print("Search text:", search_text)
    # 点击检索按钮
    page.wait_for_selector('li[onclick="confirmFilter()"]', state="visible")
    # page.click("li.f-but li:first-child")
    page.click('li[onclick="confirmFilter()"]')
    print("Clicked search button")
    # 等待搜索结果加载
    page.wait_for_load_state("networkidle")
    print(f"Search results loaded")
    result_count = page.text_content('.total-title span')
    print("Search result count:", result_count)
    # 这里添加处理搜索结果的逻辑
    # 例如，获取搜索结果的标题
    # result_titles = page.eval_on_selector_all(".list-title", "elements => elements.map(el => el.textContent)")
    # print("Search results:", result_titles)

    # 如果需要获取更多信息，可以遍历结果并点击进入详情页
    # for i, title in enumerate(result_titles):
    #     print(f"Processing result {i + 1}: {title}")
    #     page.click(f".list-title:nth-child({i + 1})")
    #     page.wait_for_load_state("networkidle")
    #     # 在这里处理详情页的内容
    #     page.go_back()
    #     page.wait_for_load_state("networkidle")

    time.sleep(5)  # 等待5秒，以便查看结果
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)