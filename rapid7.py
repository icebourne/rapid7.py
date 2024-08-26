import time
import pandas as pd
from lxml import etree
from retrying import retry
import requests
import warnings
import re
from datetime import datetime, timedelta

from dateutil import parser
import pytz
import os

n = 'rapid7'
filter = '/blog'
File_name = n + '.xlsx'
path = 'https://www.rapid7.com/blog/'

link_path = '/html/body/div[2]/div/div[2]/div[2]/section/div/div[2]/div[1]//a/@href'

title_path = '/html/body/div[2]/div/div[2]/div[2]/section/div/div/div[1]/div[1]/div[1]/h1'

author_path = '/html/body/div[2]/div/div[2]/div[2]/section/div/div/div[1]/div[1]/div[1]/div/ul[1]/li[3]/a'
time_path = '/html/body/div[2]/div/div[2]/div[2]/section/div/div/div[1]/div[1]/div[1]/div/ul[1]/li[1]'
label_path = '//*[@id="post-bottom-info"]/div/div[1]/div/div/ul/li/a' #

content_path = '/html/body/div[2]/div/div[2]/div[2]/section/div/div/div[1]/div[1]/div[2]/'

url = ['https://www.rapid7.com/blog/posts']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


@retry(stop_max_attempt_number=3)
def get_tree(url):
    # session = HTMLSession()

    # #get
    # response = session.get(url)
    # response.encoding = 'utf-8'
    # html = response.html.render()
    res = requests.get(url, headers=headers, timeout=3000)

    # 自动分析网页内容的编码方式
    res.encoding = res.apparent_encoding
    res_text = res.text
    # 解析网页
    tree = etree.HTML(res_text)
    return tree


def filter_blog_links(links):
    if filter in links.lower():  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return links


# 标签


def convert_author_names(text):
    # 替换“&”为逗号
    text = text.replace("&", ",")
    # 替换“and”前后有空白字符的情况
    text = text.replace(" and ", ",")
    text = text.replace("By", "")
    return text.strip()


def convert_date(date_str):
    # 解析日期字符串
    if "Today" in date_str:
        date_str=datetime.today().strftime('%B %d, %Y')
    if "Yesterday" in date_str:
        date_str = (datetime.today() - timedelta(days=1)).strftime('%B %d, %Y')
    date_obj = parser.parse(date_str)
    
    # 将日期时间转换为北京时间（UTC+8）
    beijing_tz = pytz.timezone('Asia/Shanghai')
    date_obj = date_obj.astimezone(beijing_tz)
    
    # 格式化为 ISO 8601 格式
    formatted_date = date_obj.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    # 在时区前加上冒号，使其符合 ISO 8601 标准
    formatted_date = formatted_date[:22] + ':' + formatted_date[22:]
    return formatted_date


def replace_str(text):
    for s in ['\r', '\t', '\n', '\\']:
        text = text.replace(s, '')
        text = re.sub(r'[^\x00-\x7F]', '', text)
    return text



def article_info():
    origin_List = []
    for i in url:
        tree = get_tree(i)
        # print(tree)
        for j in tree.xpath(link_path):
            if j not in origin_List:
                origin_List.append(j)


    Link_list = []
    for i in origin_List:
        if filter_blog_links(i):
            i=i.replace("../", '')
            Link_list.append('https://www.rapid7.com'+i)
            # Link_list.append(i)
            

    data_list=[]
    for j in Link_list:
        time.sleep(0.5)
        news_tree = get_tree(j)
        try:
            title = news_tree.xpath(title_path + "/text()")[0]
            
            # title = (','.join(title))
            # title=replace_str(title)
        except:
            continue
        
        try:
            author = news_tree.xpath(author_path + "/text()")
        
            author=convert_author_names(','.join(author))
            # author=convert_author_names(','.join(author))
        except:
            author = ''
        try:
            release_time = news_tree.xpath(time_path + "/text()")[0]
           
            release_time = convert_date(release_time)
        except:
            release_time = ''

        try:
            label = news_tree.xpath(label_path + "/text()")
            label=(','.join(label))
            print(label)
        
            # label = replace_str(label)
        except:
            label = ''

        try:
            content = news_tree.xpath(content_path + "/text()")
            # content= replace_str(''.join(content))
            content = replace_str(''.join(content))
        except:
            content = ''
       
        info = {'原标题': title,
                "url": j,
                "原标签": label,
                "作者": author,
                "原正文": content,
                "发布时间": release_time,
                "标题": "",
                "正文": "",
                "标签": "",
                "原文链接": "",
                "数据来源": n
                }
        
    #     #     data_list.append(info)
        yield info
#     # pd.DataFrame(data_list).to_excel(File_name, index=False)


def main():
    return list(article_info())
    

