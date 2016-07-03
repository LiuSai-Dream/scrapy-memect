#!/usr/bin/env python
# coding=utf-8

import logging
import pickle
from scrapy.http import Request
from scrapy.spiders import CrawlSpider, Rule
from memect.items import MemectItem
from memect.constants import *

logger = logging.getLogger(__name__)

class MlmemectSpider(CrawlSpider):
    
	# Name of  the spider
	name = "memect"
	allow_domain = ['ml.memect.com/', 'py.memect.com/', 'web.memect.com/', 'bd.memect.com/', 'app.memect.com/']
	start_urls = ['http://ml.memect.com/', 'http://py.memect.com/', 'http://web.memect.com/', 'http://bd.memect.com/', 'http://app.memect.com/']
	crawl_date = None
	crawl_date_file = "crawl_date.pkl"


	# Instance varibales
	def __init__(self):
		self.author_img_url = "profile_image"
		self.pub_time = "datetime"
		self.keywords = "keywords"
		self.content_text = "text"
		self.content_img_url = "original_pic"
		getPickleDate()


	def parse(self, response):
		logger.debug("Parsing " + response.url)
		siteType = ""
		if response.url == self.start_urls[0] :
			siteType = ML
		elif response.url == self.start_urls[1]:
			siteType = PY
		elif response.url == self.start_urls[2]:
			siteType = WEB
		elif response.url == self.start_urls[3]:
			siteType = BD
		elif response.url == self.start_urls[4]:
			siteType = APP

		if (response.status == 200):
			for link in response.xpath("//a[contains(@href,'long')]/@href").extract()[::-1]:
				yield Request(url = link, callback = self.parse_content, meta = {'siteType' : siteType})
		#	yield Request(url = response.xpath("//a[contains(@href, 'long')]/@href").extract_first(), callback = self.parse_content)
		else:
			logger.error(".........Error: Fail to fetch " + response.url + ".........")


	def getPickleDate(self):
		global crawl_date
		try:
			with open(crawl_date_file, "rb") as handle:
				crawl_date = pickle.load(handle)
			logger.debug(".........Loading pickfile " + crawl_date_file + " successfully !  " + crawl_date + ".........")
		except:
			crawl_date = {ML:"2016-06-13", PY:"2016-06-13", ML:"2016-06-13", BD:"2016-06-13", APP:"2016-06-13"}
			logger.error(".........Error: loading pickfile " + crawl_date_file + "; use default date.........")
	

	def savePickleDate(self):
		try:
			with open(crawl_date_file, "wb") as handle:
				pickle.dump(crawl_date, handle)
			logger.debug(".........Dumping pickfile " + crawl_date_file + " successfully !  " + crawl_date + ".........")
		except:
			logger.error(".........Error: dumping pickfile " + crawl_date_file + ".........")


	def need_crawl(self, siteType, curDate):
		ret = False
		global crawl_date
		if siteType == ML :
			if crawl_date[ML] > curDate:
				ret = True 
				crawl_date[ML] = curDate
		elif siteType == PY:
			if crawl_date[PY] > curDate:
				ret = True
				crawl_date[PY] = curDate
		elif siteType == WEB:
			if crawl_date[WEB] > curDate:
				ret = True
				crawl_date[WEB] = curDate
		elif siteType == BD:
			if crawl_date[BD] > curDate:
				ret = True
				crawl_date[BD] = curDate
		elif siteType == APP:
			if crawl_date[APP] > curDate:
				ret = True
				crawl_date[APP] = curDate
		if ret:
			savePickleDate()
		return ret

	def parse_content(self, response):
		logger.debug("Parsing: " + response.url)
		if (response.status != 200):
			logger.error(".........Error: Fail to fetch url!  " + response.url +".........")
			return

		siteType = response.meta['siteType']

		# Getting the date, for selecting thread next
		curDate = response.xpath('//body//span[contains(@id, "date")]/text()').extract_first()

		# Fail to get curdate
		if curDate == None:
			logger.error(".........Error: Fail to extract curDate! " + response.url + ".........")
			return
		if curDate < "2016-06-14" :
			return

		# Determine weather to crawl by comparing date
		if ( not need_crawl(siteType, curDate)):
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

			# Getting @{content_page_url}  
			if ( len(span) >= 2 ):
				item['content_page_url'] = span[1].xpath('@href') .extract_first()             

			# Getting @{pub_time}
			item['pub_time']  = thread.xpath( './/span//span[contains(@class,"'+self.pub_time+'")]/text() ').extract_first()  
		    
			# Getting @{keywords}
			item['keywords'] = []
			kws = thread.xpath( './/div[contains(@title, "'+self.keywords+'")]//span' )
			for kw in kws:
				item['keywords'] .append(kw.xpath('text()').extract_first())

			# Getting @{content_text}
			try :
				content_text = thread.xpath('.//div[contains(@class, "text")]/text()').extract_first()                       
				content_text  = content_text.strip() + " "
		        
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

			yield item
