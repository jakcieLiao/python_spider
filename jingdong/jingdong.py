import re
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *
import pymongo

# 连接mongodb
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 5)


def search():
    try:
        browser.get('https://www.jd.com/')
        input_food = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#key"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button"))
        )
        input_food.send_keys('美食')
        submit.click()
        total = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1)"))
        )
        get_product()
        return total.text
    except TimeoutException:
        return search()


def next_page(page_number):
    try:
        print(page_number)
        input_page = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > a"))
        )
        input_page.clear()
        input_page.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"), str(page_number))
        )
        get_product()
    except TimeoutException:
        next_page(page_number)


def get_product():
    """
    使用pyquery解析html，获取每一条美食信息的数据
    :return:
    """
    wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#J_goodsList .gl-warp.clearfix .gl-item'))
    )
    html = browser.page_source
    doc = pq(html)
    items = doc('#J_goodsList .gl-warp.clearfix .gl-item').items()
    for item in items:
        product = {
            'image': item.find('.p-img img').attr('src'),
            'price': item.find('.p-price').text()[1:],
            'commit': item.find('.p-commit').text()[:-3],
            'shop': item.find('.J_im_icon').text(),
            'title': item.find('.p-name.p-name-type-2').text()
        }
        print(product)
        save_to_mongo(product)


def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('储存到MONGODB成功', result)
    except Exception:
        print('储存到MONGODB失败', result)


def main():
    total = search()
    total = int(re.compile('(\d+)').search(total).group(1))
    for i in range(2, total+1):
        next_page(i)
    browser.close()


if __name__ == '__main__':
    main()