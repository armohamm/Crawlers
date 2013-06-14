import os
import logging
import uuid
import time
import socket
import urllib
import random
import simplejson
import json
from hotqueue import HotQueue

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from cloudlibs import proxy
from juicer.utils import get_current_timestamp, parse_date, get_datetime


DEFAULT_PORT = 62987
DEFAULT_PROXY_PORT = 3279
DEFAULT_ADDRESS = '0.0.0.0'
DEFAULT_PARALLEL = 10
DEFAULT_FLUSH_SECONDS = 300
BUZZINGA_URL = 'http://api.cloudlibs.com/buzzinga/'
BUZZINGA_APPID = '000000000000000000000001'
PROXIES_LIST = [ip.strip() for ip in urllib.urlopen('http://hosting.cloudlibs.com/static/misc/juicer_proxy_ips')]
URL = "http://search.twitter.com/search.json?rpp=500&q=%s"

define("port", default=DEFAULT_PORT, help="run on the given port", type=int)
define("address", default=DEFAULT_ADDRESS, help="Listen on this IP (Note: Do not listen on Public IP)", type=str)
define("parallel", default=DEFAULT_PARALLEL, help="Num sockets to use to flush parallely", type=int)
define("flush_seconds", default=DEFAULT_FLUSH_SECONDS, help="Num seconds to flush keyword stats", type=int)

tornado.httpclient.AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')

class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        self.handle_request()

    @tornado.web.asynchronous
    def post(self):
        self.handle_request()

    def handle_request(self):
        pass

    def done(self):
        self.finish()

class CommandHandler(tornado.web.RequestHandler):

    COMMANDS = ['stats', 'reset_keywords']

    def get(self, command):
        if command not in self.COMMANDS:
            self.write('Bad command\n')

        else:
            getattr(self, command)()

    def stats(self):

        self.write('stats:\n\tnum_active: %s\n\ttotal_keywords:%s\n\tnum_completed:%s\n' % \
            (self.application.state['num_active'], len(self.application.state['keywords']), self.application.state['num_completed']))

    def reset_keywords(self):
        p = proxy(BUZZINGA_URL, BUZZINGA_APPID)
        keywords = p.keywords.twitter_search()['result']
        #keywords = keywords.keys()
        #keywords = [{'keyword':'flipkart1', 'max_num':100000, 'max_seconds':0, 'frequency': 60, 'klout': 'ad6eey3wvu34rh3qnsv5ge3r', 'alchemy': 'c8362ec75771eb672c36c8a46d68846d7a49f575'}]
                    #{'keyword':'test asdf1', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf2', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf3', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf4', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf5', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf6', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf7', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf8', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf9', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf10', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                    #{'keyword':'test asdf11', 'max_num':100, 'max_seconds':300, 'frequency': 30}]

        current_timestamp = get_current_timestamp()
        _keywords = []
        _keywords_meta = self.application.state['keywords_meta']

        s_keywords = self.application.state['keywords']

        for keyword in keywords:
            if keyword['keyword'] in s_keywords:
                continue
            else:
                keyword['last_run'] = 0
                keyword['next_run'] = current_timestamp
                keyword['previous_max_id'] = 0
                keyword['latest_max_id'] = 0
                keyword['crawled_count'] = 0
                keyword['is_active'] = False
                _keywords.append(keyword['keyword'])
                _keywords_meta[keyword.pop('keyword')] = keyword

        self.application.state['keywords'].extend(_keywords)
        self.application.state['keywords_meta'] = _keywords_meta


        state = dict(num_active=0, tot_keywords=len(keywords), num_completed=0, num_failures=0, start_time=get_current_timestamp(), inqueue={}, keywords_meta=_keywords_meta, requests_cache=[], keywords=_keywords, default_timeout=60)

def _check_time(keyword_info, tweet_time):
    k_info = keyword_info
    _check_time = False
    if k_info['max_seconds']:
        check_time = get_current_timestamp() - k_info['max_seconds'] - 5.5*60*60
        _check_time = True if (parse_date(tweet_time) < parse_date('%s +0000' %time.ctime(check_time))) else False

    return _check_time

def _check_count(keyword_info, count):
    if keyword_info['max_num']:
        return False if keyword_info['max_num'] > count else True
    return False

def process_data(results, count, keyword_info, previous_max_id):
    final_data, spec_ids, ids = [], [], []
    _id = 0
    klout, alchemy = '', ''
    loop_break = False
    current_count = 0

    in_queue = HotQueue("input_queue", serializer=json, host="localhost", port=6379, db=0)
    klout = keyword_info['klout'] if keyword_info.has_key('klout') else ''
    alchemy = keyword_info['alchemy'] if keyword_info.has_key('alchemy') else ''

    for result in results:
        link = 'https://twitter.com/%s/status/%s' %(result['from_user'], result['id_str'])
        _id = result["id"]
        _data = {}
        _data['title'] = ''
        _data['description'] = result['text']
        _data['author'] = result['from_user_name']
        _data['created_at'] = result['created_at']
        _data['source_type'] = 'twitter'
        _data['original_data'] = result
        _data['_updated'] = get_current_timestamp()
        _data['link'] = link
        _data['uid'] = result['id']
        ids.append(_id)

        if klout:
            _data['klout'] = klout
        if alchemy:
            _data['alchemy'] = alchemy

        spec_ids.append({'uid': result['id']})
        final_data.append(_data)

        if _check_count(keyword_info, count) or previous_max_id in ids or _check_time(keyword_info, _data['created_at']):
            return _id, count, ids
        else:
            count += 1
            current_count += 1
            #in_queue.put(_data)
            #print _data['uid']
            pass

    return _id, count, current_count

def update_db(resp, keyword, state):
    print 'update_db', keyword, resp.request.url
    current_timestamp = str(get_datetime(get_current_timestamp()))
    data = simplejson.loads(resp.body)
    results = data.get('results')
    keyword_info = state['keywords_meta'][keyword]
    crawled_count = keyword_info['crawled_count']
    previous_max_id = keyword_info['previous_max_id']
    latest_max_id = keyword_info['latest_max_id']
    max_crawl = keyword_info['max_num']

    _id, crawled_count, current_count = process_data(results, crawled_count, keyword_info, previous_max_id)

    if state['keyword_stats'].has_key(keyword):
        state['keyword_stats'][keyword][current_timestamp] = current_count
    else:
        state['keyword_stats'][keyword] = {current_timestamp: current_count}

    url = 'http://search.twitter.com/search.json?rpp=2000&q=%s&max_id=%s' % (\
                    urllib.quote(keyword), _id)
    if latest_max_id != _id:
        print 'if', _id, crawled_count, get_current_timestamp()
        state['keywords_meta'][keyword]['crawled_count'] = crawled_count
        state['keywords_meta'][keyword]['latest_max_id'] = _id

        request = tornado.httpclient.HTTPRequest(url , proxy_host=random.choice(PROXIES_LIST), proxy_port=3279)
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(request, lambda update: update_db(update, keyword, state))
    else:
        print 'else', get_current_timestamp()
        state['num_active'] -= 1
        state['num_completed'] += 1
        state['keywords_meta'][keyword]['is_active'] = False
        state['keywords_meta'][keyword]['previous_max_id'] = _id
        state['keywords_meta'][keyword]['last_run'] = keyword_info['next_run']
        state['keywords_meta'][keyword]['next_run'] = keyword_info['next_run'] + keyword_info['frequency']
        ioloop = tornado.ioloop.IOLoop.instance()
        fn = lambda: refresh_keywords(state)
        ioloop.add_callback(fn)

def _fill_cache(state):
    keywords = state['keywords']
    inqueue = state['inqueue']

    cache = state['requests_cache']
    i = 0

    for keyword in keywords:
        if i >= options.parallel:
            break

        if keyword in inqueue:
            continue

        cache.append(keyword)
        i += 1

def _update_db(request, keyword, state, client):
    return(lambda: client.fetch(request, lambda r: update_db(r, keyword, state)))

def track_keywords(state):

    t1 = time.time()
    #logging.info('### tracking keywords ...')

    cache = state['requests_cache']
    inqueue = state['inqueue']

    limit = options.parallel - state['num_active']

    while limit:
        if not cache:
            _fill_cache(state)

        if not cache:
            break

        limit -= 1

        keyword = cache.pop(0)
        inqueue[keyword] = True
        state['num_active'] += 1
        state['keywords_meta'][keyword]['is_active'] = True
        state['inqueue'] = inqueue

        count = 0
        url = URL %urllib.quote(keyword)
        print url
        request = tornado.httpclient.HTTPRequest(url , proxy_host=random.choice(PROXIES_LIST), proxy_port=DEFAULT_PROXY_PORT)
        client = tornado.httpclient.AsyncHTTPClient()
        fn = _update_db(request, keyword, state, client)

        ioloop = tornado.ioloop.IOLoop.instance()
        #ioloop.add_callback(fn)
        ioloop.add_timeout(time.time() + 10, fn)

    if limit:
        ioloop = tornado.ioloop.IOLoop.instance()
        fn = lambda: refresh_keywords(state)
        #ioloop.add_callback(fn)
        ioloop.add_timeout(time.time() + state['default_timeout'], fn)


def refresh_keywords(state):
    keywords = state['keywords']
    keywords_meta = state['keywords_meta']

    if (get_current_timestamp() - state['last_flushed_at']) > options.flush_seconds:
        #flush the data
        #p = proxy(BUZZINGA_URL, BUZZINGA_APPID)
        #p.stats.add({'twitter_search': state['keyword_stats']})
        #state['keyword_stats'] = {}
        #state['last_flushed_at'] = get_current_timestamp()
        pass

    for keyword in keywords:
        keyword_info = keywords_meta[keyword]

        if not keyword_info['frequency']:
            continue

        if keyword_info['next_run'] <= get_current_timestamp() + keyword_info['frequency'] and keyword in state['inqueue'] and not keyword_info['is_active'] and keyword_info['frequency']:
            state['inqueue'].pop(keyword)

    ioloop = tornado.ioloop.IOLoop.instance()
    fn = lambda: track_keywords(state)
    ioloop.add_callback(fn)

def main():
    logging.info('starting up ...')
    logging.info('')

    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/_command/(.*)", CommandHandler),
        (r".*", MainHandler),
    ])

    p = proxy(BUZZINGA_URL, BUZZINGA_APPID)
    keywords = p.keywords.twitter_search()['result']
    #keywords = keywords.keys()
    #keywords = [{'keyword':'flipkart2', 'max_num':100000, 'max_seconds':0, 'frequency': 0, 'klout': 'ad6eey3wvu34rh3qnsv5ge3r', 'alchemy': 'c8362ec75771eb672c36c8a46d68846d7a49f575'}]
                #{'keyword':'test asdf1', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf2', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf3', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf4', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf5', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf6', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf7', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf8', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf9', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf10', 'max_num':100, 'max_seconds':300, 'frequency': 30},
                #{'keyword':'test asdf11', 'max_num':100, 'max_seconds':300, 'frequency': 30}]

    current_timestamp = get_current_timestamp()
    _keywords = []
    _keywords_meta = {}

    for keyword in keywords:
        keyword['last_run'] = 0
        keyword['next_run'] = current_timestamp
        keyword['previous_max_id'] = 0
        keyword['latest_max_id'] = 0
        keyword['crawled_count'] = 0
        keyword['is_active'] = False
        _keywords.append(keyword['keyword'])
        _keywords_meta[keyword.pop('keyword')] = keyword

    state = dict(num_active=0, tot_keywords=len(keywords), num_completed=0, num_failures=0, start_time=get_current_timestamp(), inqueue={}, keywords_meta=_keywords_meta, requests_cache=[], keywords=_keywords, default_timeout=60, keyword_stats={}, last_flushed_at=get_current_timestamp())

    application.state = state
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, options.address)

    ioloop = tornado.ioloop.IOLoop.instance()
    fn = lambda: refresh_keywords(state)
    ioloop.add_callback(fn)

    logging.info('starting ioloop ...')
    ioloop.start()

if __name__ == "__main__":
    FORMAT = "%(asctime)s %(funcName)s %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)

    main()
