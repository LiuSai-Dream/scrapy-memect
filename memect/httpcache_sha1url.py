from __future__ import print_function
import os
import gzip
from six.moves import cPickle as pickle
from importlib import import_module
from time import time
from weakref import WeakKeyDictionary
from email.utils import mktime_tz, parsedate_tz
from w3lib.http import headers_raw_to_dict, headers_dict_to_raw
from scrapy.http import Headers
from scrapy.responsetypes import responsetypes
from scrapy.utils.request import request_fingerprint
from scrapy.utils.project import data_path
from scrapy.utils.httpobj import urlparse_cached

# Not sure if this is right
from  memect.settings import MySqlConfig
from memect.constants import *
import MySQLdb
import logging


logger = logging.getLogger(__name__)

class FilesystemCacheStorage(object):

    def __init__(self, settings):
        self.cachedir = data_path(settings['HTTPCACHE_DIR'])
        self.expiration_secs = settings.getint('HTTPCACHE_EXPIRATION_SECS')
        self.use_gzip = settings.getbool('HTTPCACHE_GZIP')
        self._open = gzip.open if self.use_gzip else open

        logger.debug(" ------------------------------- httpcache init is performing ------------------------------- ")
        # Custome
        charset = "utf8"
        use_unicode = True
        self.user = MySqlConfig['user']
        self.passwd = MySqlConfig['passwd']
        self.dbname = MySqlConfig['db']
        self.host = MySqlConfig['host']
        self.charset = charset
        self.use_unicode = use_unicode
        self.conn = None
        self.cur = None 


    def open_spider(self, spider):
        logger.debug(" --------------------httpcache open_spider is performing ---------------------------------")
        try:
            self.conn = MySQLdb.connect(user = self.user, passwd = self.passwd, db = self.dbname, host = self.host , charset = self.charset, use_unicode = self.use_unicode)    
            # All operations are performed in the cursor
            self.cur = self.conn.cursor()
            logger.debug('---------------------------------from httpcache : Connecting to database successfully---------------------------------')
        except MySQLdb.Error, e:
            if (self.conn):
                self.conn.close()
            logger.debug('---------------------------------from httpcache : Fail to connect to database---------------------------------')

            try:
                     print ("--------------------------------- MySQL Error [%d]: %s ---------------------------------" % (e.args[0], e.args[1]))
            except IndexError, e:
                     print ("--------------------------------- MySQL Error: %s ---------------------------------" % str(e))
            

    def close_spider(self, spider):
        if (self.conn):
            self.conn.close()

    def map_url_hash(self, url, sha1) :
        try:
            insert_statement = """INSERT INTO sha1url ( sha1, url) VALUES (%s, %s) """
            self.cur.execute( insert_statement, (sha1, url ))
            self.conn.commit()
            logger.debug("---------------------------------Inserting item to table sha1url successfully---------------------------------")
        except MySQLdb.Error, e:
            try:
                     print ("--------------------------------- MySQL Error [%d]: %s ---------------------------------" % (e.args[0], e.args[1]))
            except IndexError, e:
                     print ("--------------------------------- MySQL Error: %s ---------------------------------" % str(e))
            logger.debug("---------------------------------Fail to insert into table sh1url!  Exception is " + str(e) + "---------------------------------")
            self.conn.rollback()

    def retrieve_response(self, spider, request):
        """Return response if present in cache, or None otherwise."""
        metadata = self._read_meta(spider, request)
        if metadata is None:
            return  # not cached
        [rpath, key] = self._get_request_path(spider, request)
        with self._open(os.path.join(rpath, 'response_body'), 'rb') as f:
            body = f.read()
        with self._open(os.path.join(rpath, 'response_headers'), 'rb') as f:
            rawheaders = f.read()
        url = metadata.get('response_url')
        status = metadata['status']
        headers = Headers(headers_raw_to_dict(rawheaders))
        respcls = responsetypes.from_args(headers=headers, url=url)
        response = respcls(url=url, headers=headers, status=status, body=body)
        return response

    def store_response(self, spider, request, response):
        """Store the given response in the cache."""
        [rpath, key] = self._get_request_path(spider, request)
        if not os.path.exists(rpath):
            os.makedirs(rpath)
        metadata = {
            'url': request.url,
            'method': request.method,
            'status': response.status,
            'response_url': response.url,
            'timestamp': time(),
        }
        with self._open(os.path.join(rpath, 'meta'), 'wb') as f:
            f.write(repr(metadata))
        with self._open(os.path.join(rpath, 'pickled_meta'), 'wb') as f:
            pickle.dump(metadata, f, protocol=2)
        with self._open(os.path.join(rpath, 'response_headers'), 'wb') as f:
            f.write(headers_dict_to_raw(response.headers))
        with self._open(os.path.join(rpath, 'response_body'), 'wb') as f:
            f.write(response.body)
        with self._open(os.path.join(rpath, 'request_headers'), 'wb') as f:
            f.write(headers_dict_to_raw(request.headers))
        with self._open(os.path.join(rpath, 'request_body'), 'wb') as f:
            f.write(request.body)
        # Saving the relation of sha1 and url to databased
        self.map_url_hash(key, request.url)

    # Specify the first two letter as the directory
    def _get_request_path(self, spider, request):
        key = request_fingerprint(request)
        return [os.path.join(self.cachedir, spider.name, key[0:2], key), key]

    def _read_meta(self, spider, request):
        [rpath, key]  = self._get_request_path(spider, request)
        metapath = os.path.join(rpath, 'pickled_meta')
        if not os.path.exists(metapath):
            return  # not found
        mtime = os.stat(rpath).st_mtime
        if 0 < self.expiration_secs < time() - mtime:
            return  # expired
        with self._open(metapath, 'rb') as f:
            return pickle.load(f)