#!/usr/bin/env python
# coding: utf8

import os.path
import logging
import datetime
import json
import feedparser
import requests
from time import time
from collections import deque
from tornado.ioloop import IOLoop
from clint.textui import progress

logging.basicConfig(filename='info.log', level=logging.DEBUG)

current = deque()

class sleep(object):

    def __init__(self, timeout):
        self.deadline = time() + timeout

    def __await__(self):
        def swith_to(coro):
            current.append(coro)
            coro.send(time())
        IOLoop.instance().add_timeout(self.deadline, swith_to, current[0])
        current.pop()
        return (yield)

def coroutine_start(run, *args, **kwargs):
    coro = run(*args, **kwargs)
    current.append(coro)
    coro.send(None)

def init_config():
    try:
        with open('config.json') as json_cfg_file:
            cfg = json.load(json_cfg_file)
        return cfg['count_item'], cfg['dir_name'], cfg['type_data'], cfg['urls'], cfg['timeout_check_urls'], cfg['timeout_check_files'], cfg['delta_stored']
    except Exception as e:
        logging.info("Error - {0} - time: {1}".format(e, format_time_stamp(time())))

def format_time_stamp(timestamp):
    try:
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logging.info("Error - {0} - time: {1}".format(e, format_time_stamp(time())))

def download_file(fname, url):
    try:
        r = requests.get(url, stream=True)
        total_length = int(r.headers.get('content-length'))
        if not os.path.isfile(fname) or (os.path.isfile(fname) and os.path.getsize(fname) < total_length):
            if os.path.isfile(fname):
                os.remove(fname)
                print('Delete {0}'.format(fname))
            print('Start download {0}'.format(fname))
            with open(fname, 'wb') as f:
                for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                print('Success download {0}'.format(fname))
    except Exception as e:
        logging.info("Error - {0} - time: {1}".format(e, format_time_stamp(time())))

async def check_urls(dir_name, count_item, type_data, urls, timeout):
    try:
        while True:
            now = await sleep(timeout)
            print('Check_urls start - {0}'.format(format_time_stamp(now)))
            for url in urls:
                d = feedparser.parse(url)
                for i in range(count_item):
                    links = d.entries[i].links
                    for l in links:
                        if l.type == type_data:
                            fname = os.path.join(dir_name, l.href.split('/')[-1])
                            download_file(fname, l.href)
            print('Check_urls end - {0}'.format(format_time_stamp(time())))
    except Exception as e:
        logging.info("Error - {0} - time: {1}".format(e, format_time_stamp(time())))

async def check_files(dir_name, timeout, delta_stored):
    try:
        while True:
            now = await sleep(timeout)
            print('Check_files start - {0}'.format(format_time_stamp(now)))
            today = datetime.date.today()
            files = [f for f in os.listdir(dir_name) if os.path.isfile(f)]
            for f in files:
                fileCreateDate = datetime.datetime.fromtimestamp(int(os.path.getctime(f))).date()
                delta = today - fileCreateDate
                if(delta.days > delta_stored):
                    print('Remove {0}'.format(os.path.basename(f)))
                    os.remove(f)
                print('{0} created at: {1} - not removed'.format(os.path.basename(f), format_time_stamp(os.path.getctime(f))))
            print('Check_files end - {0}'.format(format_time_stamp(time())))
    except Exception as e:
        logging.info("Error - {0} - time: {1}".format(e, format_time_stamp(time())))

if __name__ == '__main__':
    try:
        count_item, dir_name, type_data, urls, timeout_check_urls, timeout_check_files, delta_stored = init_config()
        coroutine_start(check_urls, dir_name, count_item, type_data, urls, timeout_check_urls)
        coroutine_start(check_files, dir_name, timeout_check_files, delta_stored)
        IOLoop.instance().start()
    except Exception as e:
        logging.info("Error - {0} - time: {1}".format(e, format_time_stamp(time())))
