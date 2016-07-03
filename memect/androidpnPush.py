# -*- coding: utf-8 -*-
"""
Created on Sun Jul 03 00:27:13 2016

@author: user
"""


from selenium import webdriver
import logging
import sys

logger = logging.getLogger(__name__)

url = "http://127.0.0.1:8080/notification.do"

def setNotification(driver, titleText, messageText, uriText):
    logger.debug("title : "+ titleText)    
    logger.debug("message : "+ messageText)        
    logger.debug("uri : "+ uriText) 
    
    title = driver.find_element_by_name("title")
    title.clear()
    title.send_keys(str(titleText).decode("utf8"))
    
    message = driver.find_element_by_name("message")
    message.clear()
    message.send_keys(str(messageText).decode("utf8"))
    
    uri = driver.find_element_by_name("uri")
    uri.clear()
    uri.send_keys(uriText)
    

def submitAndClose(driver):
    submit = driver.find_element_by_xpath("//input[contains(@type,'submit')]")
    submit.submit()

    driver.close()

class safeList(list):
    def get(self, index, default="No Value"):
        try:
            return self.__getitem__(index)
        except IndexError:            
            return default
            
def main(args):
    sl = safeList(args)
    
    driver = webdriver.PhantomJS('phantomjs')
    driver.get(url)
    
    setNotification(driver, sl.get(0), sl.get(1), sl.get(2))
    submitAndClose(driver)

if __name__ == "__main__":
    main(sys.argv[1:])
    
    