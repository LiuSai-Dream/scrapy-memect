#!/usr/bin/env python
# coding=utf-8

import logging
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

	# Instance varibales
	def __init__(self):
		self.author_img_url = "profile_image"
		self.pub_time = "datetime"
		self.keywords = "keywords"
		self.content_text = "text"
		self.content_img_url = "original_pic"
		

	def parse(self, response):
		logger.debug("The url is " + response.url)
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
			logger.error("..............................................Fail to fetch url : " + response.url + "..............................................")

	def parse_content(self, response):
		logger.debug("The url is " + response.url)
		if (response.status != 200):
			logger.error("..............................................Fail to fetch url : " + response.url +"..............................................")
			return

		# Getting the date, for selecting thread next
		curDate = response.xpath('//body//span[contains(@id, "date")]/text()').extract_first()

		# Fail to get curdate
		if curDate == None:
			logger.error("..............................................Fail to extract curDate!  The url is " + response.url + "..............................................")
			return

		# Setting filter date, for xpath selecting next
		filterDate = "day_" + curDate
        
		# Getting all threads of day curDate
		threadsSelectors = response.xpath('//body//div[contains(@class, "'+filterDate+'")]')

		siteType = response.meta['siteType']
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
				logger.debug (" ..............................................Exception in parsing content_text , Exception is  " + str(e)  + "..............................................")
			else :
				try:
					content_text_href = thread.xpath('.//div[contains(@class, "'+self.content_text+'")]//a/text()').extract_first()                           
					content_text = content_text + content_text_href.strip()	
					item['content_text'] = content_text
				except AttributeError as e:
					logger.debug ( "..............................................Exception in parsing content_url " + str(e) + ".............................................." ) 

			# Getting @{content_img_url}
			item['content_img_url'] = thread.xpath('.//div[contains(@class, "'+self.content_img_url +'")]/a/@href').extract_first()

			yield item