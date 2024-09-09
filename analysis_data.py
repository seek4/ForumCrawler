import json
from datetime import datetime


class AnalysisData:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """加载 JSON 数据文件"""
        with open(self.filename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def filter_posts_by_date(self, date):
        """根据指定日期过滤帖子"""
        filtered_posts = [post for post in self.data if post['create_time'].startswith(date)]
        return filtered_posts

    def analyze_posts(self, date):
        """分析指定日期的帖子数据"""
        posts = self.filter_posts_by_date(date)
        total_posts = len(posts)
        total_replies = sum(int(post['replies_count']) for post in posts)
        max_replies = max(int(post['replies_count']) for post in posts) if posts else 0
        min_replies = min(int(post['replies_count']) for post in posts) if posts else 0

        return {
            'total_posts': total_posts,
            'total_replies': total_replies,
            'max_replies': max_replies,
            'min_replies': min_replies
        }


# 使用示例
if __name__ == '__main__':
    analysis = AnalysisData('nga_posts.json')
    date = '24-09-09'
    stats = analysis.analyze_posts(date)
    print(f"Stats for {date}:")
    print(f"今日新增帖子: {stats['total_posts']}")
    print(f"今日新增帖子的回复: {stats['total_replies']}")
    print(f"最高回复的帖子: {stats['max_replies']}")