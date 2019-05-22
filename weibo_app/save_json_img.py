# coding: utf-8

import json
import urllib.request
import ssl
from bs4 import BeautifulSoup
import re
import random
import time
import urllib
import requests
import os
import weibo_app.config as config
from django.shortcuts import render
from django.http import HttpResponse
import json
import simplejson
import copy
import weibo_app.gzipMiddleWare as gzipUtils
# 模拟登陆
class weibo():
    def __init__(self, username, password):
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKi    t/601.1.46 (KHTML, like Gecko) Version/9.0 '
            'Mobile/13B143 Safari/601.1]',
            'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWeb    Kit/537.36 (KHTML, like Gecko) '
            'Chrome/48.0.2564.23 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWe    bKit/537.36 (KHTML, like Gecko) '
            'Chrome/48.0.2564.23 Mobile Safari/537.36']
        self.headers = {
            'User_Agent': random.choice(self.user_agents),
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mwei    bo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
            'Origin': 'https://passport.weibo.cn',
            'Host': 'passport.weibo.cn'}
        self.post_data = {
            'username': '',
            'password': '',
            'savestate': '1',
            'ec': '0',
            'pagerefer': 'https://passport.weibo.cn/signin/welcome?entry=    mweibo&r=http%3A%2F%2Fm.weibo.cn%2F&wm=3349&vt=4',
            'entry': 'mweibo'}
        self.login_url = 'https://passport.weibo.cn/sso/login'
        self.username = username
        self.password = password
        self.session = requests.session()

    def log_in(self):
        self.post_data['username'] = self.username
        self.post_data['password'] = self.password
        response = self.session.post(self.login_url, data=self.post_data, headers=self.headers)
        if response.status_code == 200:
            print ('-'*40 + '\n')
            print ("模拟登陆成功,当前登陆账号为：" + self.username)
        else:
            raise Exception("模拟登陆失败")

url_template = "https://m.weibo.cn/api/container/getIndex?type=wb&queryVal={}&containerid=100103type=2%26q%3D{}&page={}"
url_detail = "https://m.weibo.cn/detail/"

def header_code(header_url):
    """模拟浏览器及代理IP"""
    enable_proxy = True
    proxy_handler = urllib.request.ProxyHandler({'http': '39.137.46.70:80'})
    null_proxy_handler = urllib.request.ProxyHandler({})
    if enable_proxy:
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener(null_proxy_handler)
    urllib.request.install_opener(opener)

    ssl._create_default_https_context = ssl._create_unverified_context
    url = header_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    # 这里要注意，必须使用url=url，headers=headers的格式，否则回报错，无法连接字符
    response = urllib.request.urlopen(req)  # 注意，这里要用req，不然就被添加useragent
    htmlpage = response.read().decode('utf-8')
    soup = BeautifulSoup(htmlpage, 'html.parser')
    # print(str(soup))
    strsoup = str(soup)
    res_tr = r'<script>.*?</script>'
    m_tr = re.findall(res_tr, strsoup, re.S | re.M)
    return m_tr

def Get_img_url(mid_img_url,img_path,keys):
    """获取图片"""
    img_url = header_code(mid_img_url)
    weibo_text = re.sub(r'<.*?>', '', str(img_url))
    pattern = re.findall(r'"pics":.*?([\s\S]*?)"bid":', str(weibo_text), re.S | re.M)
    pic_url = re.findall(r'"url":.*?([\s\S]*?)"size":', str(pattern), re.S | re.M)
    picre_url = re.findall(r'https://wx\d.sinaimg.cn/orj360/.*?.jpg', str(pic_url), re.S | re.M)
    imgList = picre_url
    item=0
    imgDir = config.imgDir
    foot_path=imgDir+keys+'/'
    for item,imgPath in enumerate(imgList):
        try:
            pic = requests.get(imgPath, timeout=15)
            weibo_pic_path = foot_path+img_path+'/'
            isExists = os.path.exists(weibo_pic_path)  # Determine whether the path exists
            if not isExists:
                os.makedirs(weibo_pic_path)
                # print(weibo_pic_path + ' 创建成功')
                pass
            else:
                pass
            string = foot_path+img_path+'/' + str(item + 1) + '.jpg'
            with open(string, 'wb') as f:
                f.write(pic.content)
                print('成功下载第%s张图片: %s' % (str(item + 1), str(imgPath)))
                # print(string)
        except Exception as e:
            # print('下载第%s张图片时失败: %s' % (str(item + 1), str(imgPath)))
            print(e)
            continue
    # return True

def clean_text(text):
    """清除文本中的标签等信息"""
    dr = re.compile(r'(<)[^>]+>', re.S)
    dd = dr.sub('', text)
    dr = re.compile(r'#[^#]+#', re.S)
    dd = dr.sub('', dd)
    dr = re.compile(r'@[^ ]+ ', re.S)
    dd = dr.sub('', dd)
    return dd.strip().rstrip('全文')

def remove_duplication(mblogs):
    """根据微博的id对微博进行去重"""
    mid_set = {mblogs[0]['mid']}
    new_blogs = []
    for blog in mblogs[1:]:
        if blog['mid'] not in mid_set:
            new_blogs.append(blog)
            mid_set.add(blog['mid'])
    return new_blogs

def fetch_pages(query_val, page_num):
    """抓取关键词多页的数据"""
    mblogs = []
    for page_id in range(1 + page_num + 1):
        try:
            mblogs.extend(fetch_data(query_val, page_id))
        except Exception as e:
            print(e)
    # print("去重前：", len(mblogs))
    mblogs = remove_duplication(mblogs)
    # print("去重后：", len(mblogs))
    return mblogs

def fetch_data(query_val, page_id):
    """抓取关键词某一页的数据"""
    resp = requests.get(url_template.format(query_val, query_val, page_id))
    card_group = json.loads(resp.text)['data']['cards'][0]['card_group']
    # print('url：', resp.url, ' --- 条数:', len(card_group))
    # header = {"关键字": query_val}
    mblogs = []  # 保存处理过的微博

    for card in card_group:
        mblog = card['mblog']
        detail_url = url_detail + mblog['id']
        img_url = Get_img_url(detail_url, str(mblog['user']['screen_name']), query_val)
        blog = {
                "mid": int(mblog['id']),  # 微博id
                }
        mblogs.append(blog)
        # result = copy.deepcopy(mblogs)
    return mblogs

def remove_duplication(mblogs):
    """根据微博的id对微博进行去重"""
    mid_set = {mblogs[0]['mid']}
    new_blogs = []
    for blog in mblogs[1:]:
        if blog['mid'] not in mid_set:
            new_blogs.append(blog)
            mid_set.add(blog['mid'])
    return new_blogs

def fetch_pages(query_val, page_num):
    """抓取关键词多页的数据"""
    mblogs = []
    for page_id in range(1 + page_num + 1):
        try:
            mblogs.extend(fetch_data(query_val, page_id))
        except Exception as e:
            print(e)
    mblogs = remove_duplication(mblogs)
    return mblogs

def Down_img(request,keys,page_num):
    result=fetch_pages(keys, int(page_num))
    return render(request, "Getimg.html")


