import requests
from urllib.parse import urlencode
from requests import codes
import os
from hashlib import md5
from multiprocessing.pool import Pool
import re


def get_page(offset):
    headers = {
        'cookie':your cookie,
        'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'x-requested-with':'XMLHttpRequest',
        'referer':'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D'
    }
    params = {
        'aid':'24',
        'app_name':'web_search',
        'offset':offset,
        'format':'json',
        'keyword':'街拍',
        'autoload':'true',
        'count':'20',
        'en_qc':'1',
        'cur_tab':'1',
        'from':'search_tab',
        'pd': 'synthesis'
    }

    base_url = 'https://www.toutiao.com/api/search/content/?'
    url = base_url + urlencode(params)
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
    except requests.ConnectionError:
        return None

def get_images(json):
    if json.get('data'):
        data = json.get('data')
        for item in data:
            if item.get('title') is None:
                continue
            title = re.sub('[\t]', '', item.get('title'))
            images = item.get('image_list')
            for image in images:
                origin_image = re.sub("list.*?pgc-image", "large/pgc-image", image.get('url'))
                yield {
                    'image': origin_image,
                    'title': title
                }

def save_image(item):
    img_path = 'img0907777' + '/' + item.get('title')
    if '|' or '?' in img_path:                       
        img_path = img_path[-5:]
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        resp = requests.get(item.get('image'))
        if 200 == resp.status_code:
            file_path = img_path + '/' + '{file_name}.{file_suffix}'.format(
                file_name=md5(resp.content).hexdigest(),
                file_suffix='jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(resp.content)
                print('Downloaded image path is %s' % file_path)
            else:
                print('Already Downloaded', file_path)
    except Exception as e:
        print(e)


def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        save_image(item)

GROUP_START = 0
GROUP_END = 20


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END)])
    pool.map(main, groups)
    pool.close()
    pool.join()

