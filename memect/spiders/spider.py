#!/usr/bin/env python
# coding=utf-8

import logging
import pickle
from datetime import timedelta, date, datetime
from scrapy.http import Request, FormRequest
from scrapy.spiders import CrawlSpider, Rule
from memect.items import MemectItem
from memect.constants import *

logger = logging.getLogger(__name__)

class MlmemectSpider(CrawlSpider):
    
	# Name of  the spider
	name = "memect"
	allow_domain = ['ml.memect.com/', 'py.memect.com/', 'web.memect.com/', 'bd.memect.com/', 'app.memect.com/']
	# start_urls = ['http://ml.memect.com/', 'http://py.memect.com/', 'http://web.memect.com/', 'http://bd.memect.com/', 'http://app.memect.com/']
	start_urls = ['http://forum.memect.com/blog/thread/web-', 'http://forum.memect.com/blog/thread/ml-', 'http://forum.memect.com/blog/thread/app-', 'http://forum.memect.com/blog/thread/bd-', 'http://forum.memect.com/blog/thread/py-']

	# Instance varibales
	def __init__(self):
		self.author_img_url = "profile_image"
		self.pub_time = "datetime"
		self.keywords = "keywords"
		self.content_text = "text"
		self.content_img_url = "original_pic"

		self.crawl_date = None
		self.crawl_date_file = "crawl_date.pkl"
		self.getPickleDate()


	def getRangeDate(self, startDate, endDate):
		gapDates = []
		for gap in range(1, int((endDate - startDate).days)):
			gapDates.append((startDate + timedelta(gap)).strftime("%Y-%m-%d"))
		return gapDates

	def start_requests(self):
		endDate = datetime.now().date()
		startDate = None
		for url in self.start_urls:
			if 'ml' in url:
				datetime.strptime(self.crawl_date[ML], "%Y-%m-%d").date()
			elif 'py' in url:
				startDate = datetime.strptime(self.crawl_date[PY], "%Y-%m-%d").date()
			elif 'app' in url:
				startDate = datetime.strptime(self.crawl_date[APP], "%Y-%m-%d").date()	
			elif 'bd' in url:
				startDate = datetime.strptime(self.crawl_date[BD], "%Y-%m-%d").date()
			elif 'web' in url:
				startDate = datetime.strptime(self.crawl_date[WEB], "%Y-%m-%d").date()

			gapDates = self.getRangeDate(startDate, endDate)
			for gapDate in gapDates:
				yield FormRequest(url + gapDate, callback = self.parse_content)

	
	def getPickleDate(self):
		try:
			with open(self.crawl_date_file, "rb") as handle:
				self.crawl_date = pickle.load(handle)
			logger.debug(".........Loading pickfile " + self.crawl_date_file + " successfully !  " + self.crawl_date + ".........")
		except:
			self.crawl_date = {ML:"2016-06-13", PY:"2016-06-13", WEB:"2016-06-13", BD:"2016-06-13", APP:"2016-06-13"}
			logger.error(".........Error: loading pickfile " + self.crawl_date_file + "; use default date.........")
	

	def savePickleDate(self):
		try:
			with open(self.crawl_date_file, "wb") as handle:
				pickle.dump(self.crawl_date, handle)
			logger.debug(".........Dumping pickfile " + self.crawl_date_file + " successfully !  " + self.crawl_date + ".........")
		except:
			logger.error(".........Error: dumping pickfile " + self.crawl_date_file + ".........")


	def need_crawl(self, siteType, curDate):
		ret = False
		if siteType == ML :
			if self.crawl_date[ML] > curDate:
				ret = True 
				self.crawl_date[ML] = curDate
		elif siteType == PY:
			if self.crawl_date[PY] > curDate:
				ret = True
				self.crawl_date[PY] = curDate
		elif siteType == WEB:
			if self.crawl_date[WEB] > curDate:
				ret = True
				self.crawl_date[WEB] = curDate
		elif siteType == BD:
			if self.crawl_date[BD] > curDate:
				ret = True
				self.crawl_date[BD] = curDate
		elif siteType == APP:
			if self.crawl_date[APP] > curDate:
				ret = True
				self.crawl_date[APP] = curDate
		if ret:
			self.savePickleDate()
		return ret

	def parse_content(self, response):
		logger.debug("Parsing content: " + response.url)
		if (response.status != 200):
			logger.error(".........Error: Fail to fetch url!  " + response.url +".........")
			return

		if 'ml' in response.request.url:
			siteType = ML
		elif 'py' in response.request.url:
			siteType = PY
		elif 'app' in response.request.url:
			siteType = APP
		elif 'bd' in response.request.url:
			siteType = BD
		elif 'web' in response.request.url:
			siteType = WEB

		# Getting the date, for selecting thread next
		curDate = response.xpath('//body//span[contains(@id, "date")]/text()').extract_first()

		# Fail to get curdate
		if curDate == None:
			logger.error(".........Error: Fail to extract curDate! " + response.url + ".........")
			return

		# Determine weather to crawl by comparing date
		if ( not self.need_crawl(siteType, curDate)):
				logger.debug("Date " + curDate + " need not to crawl!")
				return

		# Setting filter date, for xpath selecting next
		filterDate = "day_" + curDate
        
		# Getting all threads of day curDate
		threadsSelectors = response.xpath('//body//div[contains(@class, "'+filterDate+'")]')

		# Interating all threads
		for thread in threadsSelectors:
		# for thread in threadsSelectors[1:5]:
			# One thread one Item
			item = MemectItem()
			item['author_name'] = None
			item['author_page_url'] = None
			item['author_img_url'] = None
			item['pub_time'] = None
			item['keywords'] = None
			item['content_text'] = None
			item['content_page_url'] = None
			item['content_img_url'] = None
			item['site_type'] = siteType

			# Getting @{author_img_url}
			item['author_img_url'] = thread.xpath( './/img[contains(@class, "'+self.author_img_url+'")]/@src').extract_first()

			span = thread.xpath('.//span/span/a')           

			# Getting  @{author_page_url} and @{author_name}
			if (len(span) >= 1 ):

				item['author_page_url'] = span[0].xpath('@href').extract_first()             	                           	  
				item['author_name'] = span[0].xpath('@title').extract_first()

				logger.debug("author_page_url " + item['author_page_url'])
				logger.debug("author_name " + item['author_name'])

			# Getting @{content_page_url}  
			if ( len(span) >= 2 ):
				item['content_page_url'] = span[1].xpath('@href') .extract_first()   
				logger.debug("content_page_url " + item['content_page_url'])          

			# Getting @{pub_time}
			item['pub_time']  = thread.xpath( './/span//span[contains(@class,"'+self.pub_time+'")]/text() ').extract_first()  
		    
			# Getting @{keywords}
			item['keywords'] = []
			kws = thread.xpath( './/div[contains(@title, "'+self.keywords+'")]//span' )
			for kw in kws:
				item['keywords'] .append(kw.xpath('text()').extract_first())

			content_page_url
			# Getting @{content_text}
			try :
				content_text = thread.xpath('.//div[contains(@class, "text")]/text()').extract_first()                       
				content_text  = content_text.strip() + " "

		        logger.debug("content_text " + content_text)   
			except AttributeError as e:
				logger.debug (" .........Exception: parsing content_text; " + str(e)  + ".........")
			else :
				try:
					content_text_href = thread.xpath('.//div[contains(@class, "'+self.content_text+'")]//a/text()').extract_first()                           
					content_text = content_text + content_text_href.strip()	
					item['content_text'] = content_text
				except AttributeError as e:
					logger.debug ( ".........Exception: parsing content_url; " + str(e) + "........." ) 

			# Getting @{content_img_url}
			item['content_img_url'] = thread.xpath('.//div[contains(@class, "'+self.content_img_url +'")]/a/@href').extract_first()
			logger.debug("content_img_url " + item['content_img_url'])  
			yield item