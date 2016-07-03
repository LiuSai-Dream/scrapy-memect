# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from memect.settings import MySqlConfig
from memect.constants import *
import MySQLdb
import logging

logger = logging.getLogger(__name__)

class MemectPipelineStore(object):
	def __init__(self, user, passwd, dbname, host, charset='utf-8', use_unicode=True):
		# logger.debug("..............................................init ml_memect_pipeline..............................................")
		
		self.user = user
		self.passwd = passwd
		self.dbname = dbname
		self.host = host
		self.charset = charset
		self.use_unicode = use_unicode
		self.conn = None
		self.cur = None	


	def open_spider(self, spider):
		# logger.debug('..............................................open_spider is performing..............................................')
		try:				
			# Connect to mysql database
			self.conn = MySQLdb.connect(user = self.user, passwd = self.passwd, db = self.dbname, host = self.host , charset = self.charset, use_unicode = self.use_unicode)
		
			# All operations are performed in the cursor
			self.cur = self.conn.cursor()
			
			logger.debug('Connecting to database successfully')
		except :
			if (self.conn):
				self.conn.close()
			logger.debug(" Fail to connect db and get cursor ")

	def close_spider(self, spider):
		# logger.debug('..............................................close_spider is performing..............................................')
		if (self.conn):
			self.conn.close()

	@classmethod
	def from_crawler(cls, crawler):
		#logger.debug('..............................................from_crawler is performing..............................................')
		return cls(
			user = MySqlConfig['user'],
			passwd = MySqlConfig['passwd'],
			dbname = MySqlConfig['db'],
			host = MySqlConfig['host'],
			charset = "utf8",
			use_unicode = True)

	def process_item(self, item, spider):
		# Inserting item into database as  one row
					
		if item['site_type'] == ML :
			insert_statement = """INSERT INTO ml_memect ( author_name, author_img_url, author_page_url, pub_time, keywords, content_text, content_page_url,  content_img_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """ 
		elif item['site_type'] == PY:
			insert_statement = """INSERT INTO py_memect ( author_name, author_img_url, author_page_url, pub_time, keywords, content_text, content_page_url,  content_img_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """ 
		elif item['site_type'] == WEB:
			insert_statement = """INSERT INTO web_memect ( author_name, author_img_url, author_page_url, pub_time, keywords, content_text, content_page_url,  content_img_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """ 
		elif item['site_type'] == BD:
			insert_statement = """INSERT INTO bd_memect ( author_name, author_img_url, author_page_url, pub_time, keywords, content_text, content_page_url,  content_img_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """ 
		elif item['site_type'] == APP:
			insert_statement = """INSERT INTO app_memect ( author_name, author_img_url, author_page_url, pub_time, keywords, content_text, content_page_url,  content_img_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """ 
		try:
			self.cur.execute(insert_statement, (item['author_name'], item['author_img_url'], item['author_page_url'], item['pub_time'], item['keywords'], item['content_text'], item['content_page_url'], item['content_img_url'] ))
			self.conn.commit()
			logger.debug(".........Inserting item to table memect successfully.........")
		except MySQLdb.Error, e:
			try:
       				 print ("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
    			except IndexError:
       				 print ("MySQL Error: %s" % str(e))
			logger.debug(".........Fail to insert into table memect!  Exception is " + str(e) + ".........")
			logger.debug(".........The insert_statement is " + insert_statement + ".........")
			self.conn.rollback()

