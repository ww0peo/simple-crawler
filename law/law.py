# -*- coding = utf-8 -*-
# @Time : 2021/10/25 14:08
# @Author : zdd
# @File : law.py
# @Software : PyCharm



import urllib.request
import urllib.parse
import json

def main():
    url = "https://flk.npc.gov.cn/api/?type=dfxfg&searchType=title%3Baccurate&sortTr=f_bbrq_s%3Bdesc&gbrqStart=&gbrqEnd=&sxrqStart=&sxrqEnd=&sort=true&size=10&_=1635142000499&page="
    for i in range(1, 50):
        next_url = url + str(i)
        json_str = askForJson(next_url)
        law_dict = json.loads(json_str)
        law_array = law_dict["result"]["data"]
        for law in law_array:
            print(law)

def askForJson(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36 SLBrowser/6.0.1.6181"
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


if __name__ == '__main__':
    main()