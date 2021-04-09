"""
This is a website scraper which designed to scrape content from assigned cnn urls. Contents crawled will be save in txt.
"""

import bs4 as bs
import urllib.request
import re
import requests
import codecs
import os
import queue as Queue
import threading
import time
from contextlib import closing


def search_video_id(soup):
    """
    Obtain video id in website.
    :param soup: url object
    :return:
    """
    pattern = re.compile(r"var configObj = {(.*?)video: '(.*?)'(.*?)}", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    video_id = pattern.search(script.text).group(2)
    return video_id


def search_video_url(video_id):
    """
    Request video base on video id.
    :param video_id: the only id of assigned video
    :return: video url and video length
    """
    # make up video url
    # example: https://fave.api.cnn.io/v1/video?id=health/2018/09/05/emirates-passenger-larry-coben-jfk-airport-vpx.hln&customer=cnn&edition=domestic&env=prod
    home_url = "https://fave.api.cnn.io/v1/video?"
    attribute_url = "&customer=cnn&edition=domestic&env=prod"
    request_url = home_url + "id=" + video_id + attribute_url

    print(request_url)
    sauce = urllib.request.urlopen(request_url).read()
    soup = bs.BeautifulSoup(sauce, 'lxml')
    reply = soup.text

    # pick up video url
    pattern = re.compile(r"(.*?)\"fileUri\":\"(.*?)\"(.*?)", re.MULTILINE | re.DOTALL)
    result = re.findall(pattern, reply)
    video_url = result[3][1] # result contains five urls, concrete example can be seen from above url

    # remove 'master.m3u8?__b__=650' in video_url
    video_url = video_url[:-22]
    print(video_url)

    # pick up video length
    pattern1 = re.compile(r"(.*?)\"length\":\"(.*?)\"(.*?)", re.MULTILINE | re.DOTALL)
    result1 = re.findall(pattern1, reply)
    video_length = result1[0][1] # result contains five urls, concrete example can be seen from above url

    return video_url, video_length


def download_video_segment(video_url, video_path):
    """
    download video segment
    :param video_url: video segment url
    :param video_path: video segment save path
    :return:
    """
    # with closing(requests.get(video_url, stream=True)) as r:
    #     chunk_size = 1024
    #     with open(video_path, "wb") as f:
    #         for chunk in r.iter_content(chunk_size=chunk_size):
    #             f.write(chunk)
    data_res = requests.get(video_url, stream=True)
    data = data_res.content
    file = codecs.open(video_path, "wb")
    file.write(data)
    return


def download_video(video_url, video_length, video_path):
    """
    carve up video into segments and download
    :param video_url: video website url
    :param video_length: video length(time)
    :param video_path: video save path
    :return:
    """
    time_list = video_length.split(":")
    hour = time_list[0]
    minute = time_list[1]
    whole_length = int(hour) * 60 + int(minute)
    segments_num = int(whole_length / 10)

    for i in range(segments_num):
        url = video_url + "/segment" + str(i+1) + "_0_av.ts"
        print(url)
        download_video_segment(url, video_path + "\segment" + str(i+1) + ".ts")

    return


def scrap_content(url, save_path):
    """
    Scrape assigned contents from provided url.
    :param url: used for scrape
    :param save_path: save content scrapped from website
    :return: attributes of a website
    """
    try:
        # Capture the whole contents from url
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
        print("url is", url)

        # title
        title = soup.h1.string
        title_file = codecs.open(save_path + "/title.txt", 'a', encoding='utf-8')
        title_file.write(title)

        # highlight
        highlights_manager = soup.select('.el__storyhighlights__item')
        highlight_file = codecs.open(save_path + "/highlight.txt", 'a', encoding='utf-8')
        for child in highlights_manager:
            highlight = child.string
            highlight_file.write(highlight + ".")

        # article
        articles_manager = soup.select('.zn-body__paragraph')
        article_file = codecs.open(save_path + "/artitle.txt", 'a', encoding='utf-8')
        article_file_subsection = codecs.open(save_path + "/artitle_section.txt", 'a', encoding='utf-8')
        for child in articles_manager:
            segment = child.text
            article_file.write(segment)
            article_file_subsection.write(segment+"\n")

        # video
        video_id = search_video_id(soup)
        video_url, video_length = search_video_url(video_id)
        os.makedirs(save_path + "/video")  # make video folder
        download_video(video_url, video_length, save_path + "/video")

        # related articles
        related_article_file_url = codecs.open(save_path + "/related.url.txt", 'a', encoding='utf-8')
        related_article_file_contents = codecs.open(save_path + "/related.content.txt", 'a', encoding='utf-8')
        results = soup.select(".el__storyelement__header")
        for i in range(len(results)):
            if i == 0:
                continue
            result = results[i]
            tmp = result.contents[0]
            url = tmp.attrs['href']
            url = "https://www.cnn.com" + url
            content = tmp.text[1:-1]
            related_article_file_url.write(url + "\n")
            related_article_file_contents.write(content + "\n")

    except (TypeError, AttributeError) as e:
        print("Errors!", e)

    return


def url_lead(url_file_path):
    """
    read in url list, which is already crawled
    :param url_file_path:
    :return:
    """
    file = codecs.open(url_file_path).read().split("\n")
    url_queue = Queue.Queue(len(file))
    for url in file:
        url_queue.put(url)
    return url_queue


def assign_scrape(url_queue, lock, save_path):
    """
    assign task for every thread
    :param url_queue:  a queue contains all urls
    :param lock: lock in thread for using one global variation
    :param save_path: save scrapping contents
    :return:
    """
    global count
    while not exitFlag:
        lock.acquire()
        if not url_queue.empty():
            count += 1
            lock.release()

            url = url_queue.get()
            new_path = save_path + r"/" + str(count)
            os.makedirs(new_path)
            scrap_content(url, new_path)
        else:
            lock.release()


def make_threads(thread_num, url_queue, save_path):
    """
    makeup threads and scrape contents from assigned url
    :param thread_num: threads number
    """
    print("makeup threads")
    lock = threading.Lock()
    for i in range(thread_num):
        print("start thread", i)
        thread = threading.Thread(target=assign_scrape, args=(url_queue, lock, save_path))
        thread.start()




count = 241# example number
exitFlag = 0 # flag for url_queue
url_queue = url_lead("url_cnn_filter.txt")
make_threads(1, url_queue, r"")
# make sure url queue is empty
while not url_queue.empty():
    pass
exitFlag = 1

