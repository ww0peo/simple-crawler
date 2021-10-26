# -*- coding = utf-8 -*-
# @Time : 2021/10/26 14:22
# @Author : zdd
# @File : git.py
# @Software : PyCharm

import json
from lxml import etree
import urllib.request
import time
import sys, getopt
import datetime

def main(argv):
    url = ''
    start_time = ''
    try:
        opts, args = getopt.getopt(argv, "hu:t:", ["url=", "time="])
    except getopt.GetoptError:
        print('git.py -u <url> -t <time>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('git.py -u <url> -t <time>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
        elif opt in ("-t", "--time"):
            start_time = arg
    # getCommitMsg("http://192.168.2.134:9092/backend/citymanage/activity?limit=20&offset=", "2021-08-01 00:00:00")
    print("爬取开始")
    starttime = datetime.datetime.now()
    print("===============================================================")
    getCommitMsg(url, start_time)
    print("===============================================================")
    endtime = datetime.datetime.now()
    duringtime = endtime - starttime
    print("爬取结束")
    print("爬虫用时:%f秒"%(duringtime.seconds))


def askForJson(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36 SLBrowser/6.0.1.6181",
        "Cookie": "experimentation_subject_id=eyJfcmFpbHMiOnsibWVzc2FnZSI6IkltWmlPRFJpWmpabExUQTFNekF0TkRCa1lTMWhPREExTFdZeE1tWXpZekprTkRsak9TST0iLCJleHAiOm51bGwsInB1ciI6ImNvb2tpZS5leHBlcmltZW50YXRpb25fc3ViamVjdF9pZCJ9fQ%3D%3D--7e29157bb25c780e0c1897f6ff62dc7058b3412b; sidebar_collapsed=false; remember_user_token=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ilcxc3lObDBzSWlReVlTUXhNQ1J3V1dGbFIyNDBSeTR5UzJaaFJYVnViWGwwVWxkUElpd2lNVFl6TlRJeE1qSTVNUzQwT0RBeE1qRTBJbDA9IiwiZXhwIjoiMjAyMS0xMS0wOVQwMTozODoxMS40ODBaIiwicHVyIjoiY29va2llLnJlbWVtYmVyX3VzZXJfdG9rZW4ifX0%3D--3bffe3ff977fa12d7e65f6554c56dc53a2a2386a; _gitlab_session=6d0f630b127e14f47ab187dc9494a164; event_filter=all",
        "Referer": "http://192.168.2.134:9092/backend/citymanage/activity?limit=20&offset=60",
        "X-CSRF-Token": "1v2ELdRK9Yzw+LxjE0Ti3YhZv8tdxW+4umsUpJsq6Ga9DxgraBTADLVUZj2E5qQFMBTCkSuz+oAFT6ONX9OSeA==",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*"
    }
    request = urllib.request.Request(url=url, headers=head)
    json_str = ""
    try:
        response = urllib.request.urlopen(request)
        json_str = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return json_str

def getCommitMsg(url, start_time):
    if url is None or len(url) <= 0:
        print("请输入参数-u！")
        return
    if start_time is not None or len(start_time) > 0:
        try:
            time.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("请输入正确的时间参数-t，格式例为2020-01-01 00:00:00!")
            return
    else:
        print("请输入时间！")
        return
    offset = 0
    finished_flag = 0
    commits = []
    while 1:
        next_url = url + str(offset)
        text = askForJson(next_url)
        json_str = json.loads(text)
        html = json_str["html"]
        html = etree.HTML(html)
        commit_list = html.xpath("//div[@class='event-item']")
        for commit in commit_list:
            commit_objet = {}
            commit_content_list = commit.xpath(".//div[@class='commit-row-title']/text()")
            commit_objet["content"] = ""
            for commit_content in commit_content_list:
                commit_content = commit_content.strip()
                commit_content = commit_content.replace('\n', '')
                commit_content = commit_content.replace('.', '')
                commit_content = commit_content[1:len(commit_content)]
                if len(commit_content) != 0:
                    commit_objet["content"] = commit_content
                    break
            commit_user = commit.xpath("./div[@class='event-user-info']/span[@class='author_name']/a/text()")[0]
            commit_objet["user"] = commit_user
            if len(commit.xpath(".//div[@class='commit-row-title']/a/text()")) > 0:
                commit_objet["id"] = commit.xpath(".//div[@class='commit-row-title']/a/text()")[0]
                commit_url = commit.xpath(".//div[@class='commit-row-title']/a/@href")[0]
                commit_objet["url"] = urllib.parse.urljoin(url, commit_url)
            commit_objet["time"] = commit.xpath("./div[@class='event-item-timestamp']/time/@datetime")[0]
            if compare_time(start_time, commit_objet["time"]) > 0:
                finished_flag = 1
                break
            print(commit_objet)
            commits.append(commit_objet)
        if finished_flag == 1:
            break
        offset += 20

# 比较时间
def compare_time(time_1, time_2):
    if time_1 and time_2:
        time_stamp_1 = time.mktime(time.strptime(time_1, '%Y-%m-%d %H:%M:%S'))
        time_stamp_2 = time.mktime(time.strptime(time_2, '%Y-%m-%dT%H:%M:%SZ'))
        if int(time_stamp_1) > int(time_stamp_2):
            return 1
        else:
            return -1
    else:
        return None

if __name__ == "__main__":
    main(sys.argv[1:])