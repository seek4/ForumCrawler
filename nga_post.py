class NGAPost:
    def __init__(self, post_id, title, content, url, replies_count, create_time):
        self.post_id = post_id
        self.title = title
        self.content = content
        self.url = url
        self.replies_count = replies_count
        self.create_time = create_time

    def to_dict(self):
        return {
            "post_id": self.post_id,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "replies_count": self.replies_count,
            "create_time": self.create_time
        }