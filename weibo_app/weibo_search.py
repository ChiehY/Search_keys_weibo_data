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
    proxy_handler = urllib.request.ProxyHandler({'http':'124.205.155.157:9090'})
    null_proxy_handler = urllib.request.ProxyHandler({})
    if enable_proxy:
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener(null_proxy_handler)

    ssl._create_default_https_context = ssl._create_unverified_context
    url = header_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    # 这里要注意，必须使用url=url，headers=headers的格式，否则回报错，无法连接字符
    urllib.request.install_opener(opener)
    response = urllib.request.urlopen(req)  # 注意，这里要用req，不然就被添加useragent
    htmlpage = response.read().decode('utf-8')
    soup = BeautifulSoup(htmlpage, 'html.parser')
    # print(str(soup))
    strsoup = str(soup)
    res_tr = r'<script>.*?</script>'
    m_tr = re.findall(res_tr, strsoup, re.S | re.M)
    return m_tr

def Get_time(mid_time_url):
    """获取发布时间格式化"""
    # put_time = Get_time(m_tr)
    m_time = header_code(mid_time_url)
    weibo_text = re.sub(r'<.*?>', '', str(m_time))
    # print(weibo_text)
    pattern = re.findall(r'"created_at":.*?([\s\S]*?)"id":', str(weibo_text), re.S | re.M)
    pat_test = ((str(pattern[0]).rstrip()).rstrip('n'))
    # print(pat_test)
    re_pat = ((re.sub('\\\\', '', pat_test)).rstrip(','))
    dd = time.strptime(eval(re_pat), "%a %b %d %H:%M:%S +0800 %Y")
    re_time=time.strftime('%Y/%m/%d %H:%M:%S', dd) # strftime表示时间的格式
    return re_time

def Get_img_url(mid_img_url):
    """获取图片url"""
    img_url = header_code(mid_img_url)
    weibo_text = re.sub(r'<.*?>', '', str(img_url))
    pattern = re.findall(r'"pics":.*?([\s\S]*?)"bid":', str(weibo_text), re.S | re.M)
    pic_url = re.findall(r'"url":.*?([\s\S]*?)"size":', str(pattern), re.S | re.M)
    picre_url = re.findall(r'https://wx\d.sinaimg.cn/orj360/.*?.jpg', str(pic_url), re.S | re.M)
    imgList = picre_url
    # hyperlink_format = '<a href="{link}">{str}</a>'
    # for i in imgList:
    #   url=hyperlink_format.format(link=i, text='linky text')
    return imgList

def Get_text(mid_url):
    """获取微博全文"""
    m_tr = header_code(mid_url)

    text_re = r'<span class=\\\\"surl-text\\\\">(.*?)\\n'
    m_text = re.findall(text_re, str(m_tr), re.S | re.M)

    web_text = ((str(m_text).replace('</span></a><br />', '')).replace('<br />', '')[:-3][1:])
    # new_str = web_text.replace('<\/?span[^>]*>', '')
    weibo_text = re.sub(r'<.*?>', '', web_text).rstrip("']").rstrip().rstrip('\"').rstrip('全文').lstrip("['")
    return weibo_text

def Get_pos(pos_url):
    pos_tr = header_code(pos_url)
    weibo_text = re.sub(r'<.*?>', '', str(pos_tr))
    list=['"page_url"','"page_title"','"content1"','"content2"']
    position=[]
    is_pos = 'https://m.weibo.cn/p/index?containerid='
    for i in range(3):
        pattern = re.findall(r''+list[i]+':.*?([\s\S]*?)'+list[i+1]+':', str(weibo_text), re.S | re.M)
        if pattern:
           re_pat=((re.sub('\\\\', '', ((str(pattern[0]).rstrip()).rstrip('n')))).rstrip(','))
        else:
            re_pat=[]
        position.append(re_pat)
    if re_pat and is_pos in position[0]:
        pos = {"地址": eval(position[1]), "详细地址介绍":eval(position[2])}
    else:pos=[]
    return pos

def clean_text(text):
    """清除文本中的标签等信息"""
    dr = re.compile(r'(<)[^>]+>', re.S)
    dd = dr.sub('', text)
    dr = re.compile(r'#[^#]+#', re.S)
    dd = dr.sub('', dd)
    dr = re.compile(r'@[^ ]+ ', re.S)
    dd = dr.sub('', dd)
    return dd.strip().rstrip('全文')

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
        # print(detail_url)
        put_time = Get_time(detail_url)
        mtext = Get_text(detail_url)
        pos = Get_pos(detail_url)
        if len(mtext)<len(clean_text(mblog['text'])):
            mtext=clean_text(mblog['text'])
        elif mtext=='':
            mtext = clean_text(mblog['text'])
        else:
            mtext=mtext
        # 下载图片
        # Down_img(detail_url,str(mblog['user']['screen_name']),query_val)
        img_url = Get_img_url(detail_url)
        blog = {
                "mid": int(mblog['id']),  # 微博id
                "用户名": mblog['user']['screen_name'],  # 用户名
                "用户id": int(mblog['user']['id']),  # 用户id
                "发布时间": put_time,
                # "概要": clean_text(mblog['text']),  # 文本
                "内容": mtext,
                "配图url": img_url,
                "发布位置": pos,
                "转发数": mblog['reposts_count'],  # 转发
                "评论数": mblog['comments_count'],  # 评论
                "点赞数": mblog['attitudes_count'] # 点赞
                }
        mblogs.append(blog)
        result = copy.deepcopy(mblogs)
        # dic = {"header": header, "data": result}
    return result   #mblogs

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
        time.sleep(2)
    # print("去重前：", len(mblogs))
    mblogs = remove_duplication(mblogs)
    # print("去重后：", len(mblogs))
    return mblogs

def weibo_keys(request, *configs):
    if request.method == 'GET':
        # restful = Restful(config)
        if configs:
            keys = str(configs[0])
            page_num = int(configs[1])
            header = {"关键字": keys,"页面数":page_num}
            result = fetch_pages(keys,page_num)
            weibo_dic = {"header": header, "data": result}
            resultData = simplejson.dumps(weibo_dic,ensure_ascii=False, indent=4,separators=(',',':'))
            result = gzipUtils.jsonToGzip(resultData, keys)
            # return HttpResponse(result)
            return HttpResponse(resultData)

        else:
            return HttpResponse('configs are wrong.')

    elif request.method == 'POST':
        return HttpResponse('Method is wrong.')
    else:
        return HttpResponse('What are you doing?')