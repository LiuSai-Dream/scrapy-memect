# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from  memect.settings import MySqlConfig
from dateutil.parser import parse
import MySQLdb
import logging

logger = logging.getLogger(__name__)

class MemectPipelineProcess(object):
	def process_item(self, item, spider):

		if (item['author_name']  is not None) :
			item['author_name'] = ' '.join( item['author_name'].split()[:-1] )
			# logger.debug('author_name -- ' + item['author_name'])

		if (item['author_page_url'] is not None) :
			item['author_page_url'] = item['author_page_url'].strip()
			# logger.debug('author_page_url -- ' + item['author_page_url'])

		if (item['author_img_url'] is not None) :
			item['author_img_url'] = item['author_img_url'].strip()
			# logger.debug('author_img_url -- ' + item['author_img_url'])

		if (item['pub_time'] is not None) :
			item['pub_time'] =  parse(item['pub_time'].strip()).strftime("%Y-%m-%d %H:%M:%S")
			# logger.debug('pub_time -- ' + item['pub_time'])

		if (item['keywords'] is not None) :
			kws = item['keywords']
			item['keywords'] = ''
			for kw in kws:
				if (kw is not None) :
					item['keywords'] = item['keywords'] + ' ' + kw
			item['keywords'].strip()
			# logger.debug('keywords -- ' + item['keywords'])

		if (item['content_text'] is not None) :
			item['content_text'] = item['content_text'].strip()
			# logger.debug('content_text -- ' + item['content_text'])

		if (item['content_page_url'] is not None) :
			item['content_page_url'] = item['content_page_url'].strip()
			# logger.debug('content_page_url -- ' + item['content_page_url'])

		if (item['content_img_url'] is not None) :
			item['content_img_url'] = item['content_img_url'].strip()
			# logger.debug('content_img_url -- ' + item['content_img_url'])

		return item