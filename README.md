# 项目简介
一个爬虫学习项目，当前实现的功能是NGA论坛内容的爬取。
通过playwright浏览器,模拟真实用户请求来爬取NGA论坛前10页的帖子内容，并保存成json文件。
并进行简单的分析。

# 注意事项
该项目只用于学习，请勿从事非法内容爬取。

# 使用说明
该项目基于playwright浏览器驱动，需要安装playwright浏览器驱动。</br>
安装方式：
1. 先安装本项目所需依赖库，建议python环境3.9。不确定其他python环境的兼容性
```shell
pip install -r requirements.txt
```
2. 安装playwright浏览器驱动
```shell
playwright install
```
3. 运行爬虫程序用于爬取内容。
```shell
python grep_data_play_wright.py

# 如果想要分析,参考:
python analyze_data.py
```

# 联系我
如果有侵权或者任何疑问，请联系我haoyunyangtong AT qq邮箱
