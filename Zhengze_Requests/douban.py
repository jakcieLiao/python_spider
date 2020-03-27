# -*- coding=utf-8 -*-
import json
import requests
from requests.exceptions import RequestException
import re
from multiprocessing import Pool

"""
使用requests和正则表达式爬取豆瓣电影，同时用线程池提高效率

"""

def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}
        response = requests.get(url, headers=headers)
        # 解决中文乱码
        response.encoding = 'utf-8'
        if response.status_code == 200:
            # return response.text.encode('utf-8')
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    # 匹配排名
    # .*?   匹配字符串
    # \d    匹配数字
    # \d+   匹配任意数字
    # re.S  可以匹配任意字符，包括换行符
    pattern = re.compile('bd doulist-subject">.*?src="(.*?)"/>.*?title">.*?target="_blank">(.*?)</a>.*?'
                                  + 'rating_nums">(.*?)</span>.*?abstract">(.*?)<br />(.*?)<br />(.*?)'
                                  + '<br />(.*?)<br />(.*?)</div>.*?</time>', re.S)
    items = re.findall(pattern, html)
    # pattern_test = re.compile('bd doulist-subject">.*?src="(.*?)"/>.*?title">.*?target="_blank">(.*?)</a>.*?'
    #                           + 'rating_nums">(.*?)</span>.*?abstract">(.*?)<br />(.*?)<br />(.*?)'
    #                           + '<br />(.*?)<br />(.*?)</div>.*?</time>', re.S)
    # items_test = re.findall(pattern_test, html)
    # print(items_test)
    for item in items:
        # actor = re.compile('主演:(.*?)/n')
        yield {
            'image': item[0],
            'title': item[1],
            'score': item[2],
            'director': item[3],
            'actor': item[4],
            'type': item[5],
            'source': item[6],
            'time': item[7]
        }


def write_to_file(content):
    with open("result.txt", 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(offset):
    url = 'https://www.douban.com/doulist/1253915/?start=' + str(offset) + '&sort=seq&playable=0&sub_type='
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)
    # print(html)
    # parse_one_page(html)
    # print(html)


if __name__ == '__main__':
    # for i in range(8):
    #     main(i*25)
    # 使用进程池，爬取效率提高
    pool = Pool()
    pool.map(main, [i*25 for i in range(8)])