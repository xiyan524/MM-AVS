"""
This is a webCrawler designed for extracting urls. It will filter the desired urls to prevent
duplicated crawls in the future. Final urls will be saved in txt file.
"""

import bs4 as bs
import urllib.request
import urllib.error
import re
import codecs
import time
import socket
import threading
import queue as Queue
import urllib3



def html_to_bs(start_url):
    """
    Convert website html to Beautiful Soup.
    :param start_url: start url for crawling
    :return beautiful soup object
    """
    sauce = urllib.request.urlopen(start_url).read()
    soup = bs.BeautifulSoup(sauce, 'lxml')
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


def url_fill(spider_list, max_url_num, module_pattern):
    """
    Fill url list base on current urls.
    :param spider_list: urls obtained from start url
    :return: scape_list which contain max number url
    """
    scrape_list = [] + spider_list

    for url in spider_list:
        crawler_url = url

        try:
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 10
            time.sleep(sleep_download_time)

            sauce = urllib.request.urlopen(crawler_url).read()
            soup = bs.BeautifulSoup(sauce, 'lxml')
        except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout, AttributeError):
            print("Soup convert failed from: ", url)
            continue

        try:
            new_url_list = url_finder(soup, crawler_url, module_pattern, scrape_list)
        except Exception as e:
            print("Url find fail: " + url)
            print(str(e))

        scrape_list = new_url_list + scrape_list
        spider_list += new_url_list

        print(len(scrape_list))
        if len(scrape_list) >= max_url_num:
            break

    return scrape_list


def url_save(scrape_list, save_path):
    file = codecs.open(save_path, 'a')
    for url in scrape_list:
        file.write(str(url) + "\n")


def url_filter(url, lock, save_file_path):

    try:
        print(url)
        timeout = 50
        socket.setdefaulttimeout(timeout)
        sleep_download_time = 10
        time.sleep(sleep_download_time)

        # context = ssl._create_unverified_context()
        request = urllib.request.urlopen(url)
        sauce = request.read()
        request.close()
    except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout) as e:
        print('URL Error!', url)
        print(e)
        return

    soup = bs.BeautifulSoup(sauce, 'lxml')

    # check highlight
    highlight = soup.select('.el__storyhighlights__item')
    if len(highlight) == 0:  # there is no highlight in website
        return

    # check video
    video = soup.select('.el__video')
    if len(video) == 0:  # there is no video in website
        return

    lock.acquire()
    save_file = codecs.open(save_file_path, 'a')
    save_file.write(str(url) + "\n")
    save_file.close()
    lock.release()

# def url_lead(url_file_path):
#     """
#     read in url list, which is already crawled
#     :param url_file_path:
#     :return:
#     """
#     file = codecs.open(url_file_path).read().split("\n")
#     scrape_list = []
#     for url in file:
#         scrape_list.append(url)
#     return scrape_list

def assign_filter(url_queue, lock, save_path):
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
            url_filter(url, lock, save_path)


def make_threads(thread_num, url_queue, save_path):
    """
    makeup threads and scrape contents from assigned url
    :param thread_num: threads number
    """
    print("makeup threads")
    lock = threading.Lock()
    for i in range(thread_num):
        print("start thread", i)
        thread = threading.Thread(target=assign_filter, args=(url_queue, lock, save_path))
        thread.start()


def remove_duplicate_urls(file_path, existing_file_path, filter_file_path):
    file = codecs.open(file_path).read().split("\n")
    urls = []
    for url in file:
        urls.append(url)

    file1 = codecs.open(existing_file_path).read().split("\n")
    exist_urls = []
    for url in file1:
        exist_urls.append(url)

    urls_filter = set(urls)
    urls_exist = set(exist_urls)
    final_urls = list(urls_filter - urls_exist)

    filter_file = codecs.open(filter_file_path, 'a', encoding='utf-8')
    for url in final_urls:
        filter_file.write(url+"\n")


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


def main():
    max_url_num = 100
    start_url = "https://www.dailymail.co.uk/news/headlines/index.html?previousday=1"
    module_pattern = "news/article"
    save_path = r"daily_mail.txt"

    print("convert start url!")
    soup = html_to_bs(start_url)
    print("crawl start url!")
    spider_list = url_finder(soup, start_url, module_pattern, [])
    # print("fill url list!")
    # scrape_list = url_fill(spider_list, max_url_num, module_pattern)
    print("save file!")
    url_save(spider_list, save_path)

    # file_path = r"" # waiting for remove repetition
    # exist_file_path = r"" # existing file path
    # filter_file_path = r"" # new file without repetition
    # remove_duplicate_urls(file_path, exist_file_path, filter_file_path)
#
# exitFlag = 0  # flag for url_queue
# scrape_queue = url_lead("url_cnn.txt")
# print("start scrape")
# make_threads(1, scrape_queue, r"")
# # make sure url queue is empty
# while not scrape_queue.empty():
#     pass
# exitFlag = 1

if __name__ == "__main__":
    main()
