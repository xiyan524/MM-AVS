"""
This is a webCrawler designed for extracting urls from DM website. Final urls will be saved in txt file.
"""

import bs4 as bs
import urllib.request
import urllib.error
import re
import codecs
import os
import time
import socket
import threading
import queue as Queue
import requests
import urllib3



def html_to_bs(url):
    """
    Convert website html to Beautiful Soup.
    :param start_url: start url for crawling
    :return beautiful soup object
    """
    try:
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
    except(urllib.error.URLError):
        print("Connect error:", url)
        return None
    return soup


def url_finder(soup, start_url, module_pattern, exist_url):
    """
    Find all the url links from start url.
    :param soup: bs by start url
    start_url: start url for crawling
    module_pattern: the url pattern of assigned module
    :return: spider_lst : a list contains all urls in website
    """
    spider_list = [] + exist_url
    # spider_list.append(start_url)

    http_scan = re.compile('http')
    module_scan = re.compile(module_pattern)
    # http_full_html = "https://www.cnn.com"
    http_full_html = "https://www.dailymail.co.uk"

    tmp_url_list = soup.find_all('a')
    for link in tmp_url_list:
        new_url = link.get('href')
        full_url_flag = re.findall(http_scan, str(new_url))
        module_url_flag = re.findall(module_scan, str(new_url))

        # check url module
        if len(module_url_flag) > 0:
            # Adding url with full format to list
            if len(full_url_flag) > 0:
                if new_url not in spider_list:
                    spider_list.append(new_url)
            # Complementing url lacking http format
            else:
                new_url = http_full_html + str(new_url)
                if new_url not in spider_list:
                    spider_list.append(new_url)
        else:
            pass

    return spider_list


def url_save(scrape_list, save_path):
    file = codecs.open(save_path, 'a')
    for url in scrape_list:
        file.write(str(url) + "\n")


def url_crawler():
    max_day = 150
    module_pattern = "news/article"
    save_path = r"daily_mail.txt"

    final_url = set()
    for i in range(max_day):
        url = "https://www.dailymail.co.uk/news/headlines/index.html?previousday=" + str(i + 1)
        soup = html_to_bs(url)
        spider_list = url_finder(soup, url, module_pattern, [])
        spider_set = set(spider_list)
        tmp_final_url_list = list(spider_set - final_url)
        url_save(tmp_final_url_list, save_path)


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


def assign_task(url_queue, lock, save_path):
    """
    assign filter task for every thread
    :param url_queue:  a queue contains all urls
    :param lock: lock in thread for using one global variation
    :param save_path: save scrapping contents
    :return:
    """
    # save_file = codecs.open(save_path, 'a', encoding='utf-8')
    while not exitFlag:
        if not url_queue.empty():
            url = url_queue.get()
            extracts_contents_from_url(url, lock, save_path)


def make_threads(thread_num, url_queue, save_path):
    """
    makeup threads and scrape contents from assigned url
    :param thread_num: threads number
    """
    print("makeup threads")
    lock = threading.Lock()
    for i in range(thread_num):
        print("start thread", i)
        thread = threading.Thread(target=assign_task, args=(url_queue, lock, save_path))
        thread.start()


def check_website(soup):
    """
    make sure the assigned website contains necessary contents
    :param soup: a bs4 object of assigned website
    :return:
    """
    flag = True

    # check highlight
    highlight1 = soup.select('.mol-bullets-with-font')
    highlight2 = soup.find("div", {"itemprop": "articleBody"})
    if highlight2 is not None:
        highlight2 = highlight2.contents[1]
    if len(highlight1) == 0:
        if highlight2.name != "ul":
            flag = False

    # check video
    video = soup.find("video")
    if video is None:
        flag = False

    return flag


def extracts_contents_from_url(url, lock, save_path):
    """
    extract necessary contentes from url and download video from video path
    :param soup: bs4 object
    :param video_path: video path in current website
    :return:
    """
    global count

    print("Extract!")

    # check the website about highlight
    soup = html_to_bs(url)
    if soup is not None:
        flag = check_website(soup)

        if flag:
            # establish a file for crapped contents
            lock.acquire()
            file_path = save_path + "/" + str(count)
            count += 1
            os.makedirs(file_path)
            lock.release()

            # get title
            title_file = codecs.open(file_path + "/title.txt", 'a', encoding='utf-8')
            title = soup.h2.text
            title_file.write(title)

            # get highlight
            highlight_file = codecs.open(file_path + "/highlight.txt", 'a', encoding='utf-8')
            if len(soup.select('.mol-bullets-with-font')) != 0:
                highlight_manager = soup.select('.mol-bullets-with-font')[0].contents
            else:
                highlight_manager = soup.find("div", {"itemprop": "articleBody"}).contents[1].contents
            for child in highlight_manager:
                highlight = child.text
                highlight.replace(r"\\", "")
                highlight_file.write(highlight + "\n")

            # get article
            article_file = codecs.open(file_path + "/article.txt", 'a', encoding='utf-8')
            article_manager = soup.select(".mol-para-with-font")
            flag = True
            if len(article_manager) == 0:
                article_manager = soup.find_all("font", {"style": "font-size: 1.2em;"})
                flag = False
            for child in article_manager:
                if flag:
                    article = child.string
                else:
                    article = child.text
                if article is not None:
                    article_file.write(article)

            # get video
            video_file = codecs.open(file_path + "/video.mp4", "wb")
            video_url = soup.find("video").contents[1].attrs["src"]
            try:
                data_res = requests.get(video_url, stream=True)
                data = data_res.content
                video_file.write(data)
            except (TypeError, AttributeError, requests.ConnectionError) as e:
                print("Video download errors!", e)

            # get image and its caption
            img_caption_file = codecs.open(file_path + "/img_caption.txt", 'a', encoding='utf-8')
            img_group_manager = soup.select(".artSplitter")
            img_count = 0
            for img_group in img_group_manager:
                if img_count > 3:
                    break
                try:
                    img_caption_tag = img_group.contents[3].text
                    img_caption_file.write(img_caption_tag+"\n")
                    if img_group.contents[1].attrs['class'][0] == "mol-img":
                        img_tag = img_group.contents[1].contents[1].contents[1].attrs["data-src"]
                        img = requests.get(img_tag).content
                        img_file = file_path + "/" + str(img_count) + '.png'
                        with open(img_file, 'wb') as file:  
                            file.write(img)
                        img_count += 1
                except:
                    print("Img download errors!", img_count)



def main():
    # scrap urls from website
    # url_crawler()

    # filter urls which don't satisfy commands
    global exitFlag # flag for url_queue
    global count # number of crapped examples
    exitFlag = 0
    count = 10208

    scrape_queue = url_lead("daily_mail.txt")
    make_threads(16, scrape_queue, r"")
    # make sure url queue is empty
    while not scrape_queue.empty():
        pass
    exitFlag = 1


if __name__ == "__main__":
    main()