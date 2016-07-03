# -*- coding: utf-8 -*-
"""
Created on Sun Jul 03 00:27:13 2016

@author: user
"""


from selenium import webdriver
import logging
import sys
import MySQLdb
from  memect.settings import MySqlConfig
from datetime import datetime, date
import gc
import random
from memect.constants import *

logger = logging.getLogger(__name__)
url = "http://127.0.0.1:8080/notification.do"
cur = None
conn = None
curDate = datetime.now().date().strftime("%Y-%m-%d")

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
        
def connectMysql():
    user = MySqlConfig['user'],
    passwd = MySqlConfig['passwd'],
    dbname = MySqlConfig['db'],
    host = MySqlConfig['host'],
    charset = "utf8",
    use_unicode = True
    
    try:
        # Exceptions make it extremely difficult to clean up bu hand.
        # Manually invok python garbage collector 
        # which close off any old Mysql connections
        gc.collect()        
        
        # Connect to mysql database
        conn = MySQLdb.connect(user = user, passwd = passwd, db = dbname, host = host , charset = charset, use_unicode = use_unicode)
		
        # All operations are performed in the cursor
        cur = conn.cursor()
        logger.debug('Debug: Connecting to database successfully')
    except :
        if (conn):
            conn.close()  

def getCurDateResult():
    query = """SELECT ( author_name, author_img_url, author_page_url, pub_time, keywords, content_text, content_page_url,  content_img_url) FROM (%s) WHERE pub_time LIKE (%s) """    
    tables = ["ml_memct", "bd_memect", "app_memect", "web_memect", "py_memect"]
    results = []
        
    for table in tables:
        resultNum = cur.execute(query, (table, curDate))
        if (resultNum != 0):
            result = cur.fetchAll()
            print(result)
    else:
        logger.warn("Warning: Table ")
    return results
    
def sendNotification(results):
    sl = None
    if (len(results) <= 0):
        sl = safeList([])
    else:
        index = random.randint(0, len(results))
        sl = safeList(results[index])        
    
    # Trigger an request
    driver = webdriver.PhantomJS('phantomjs')
    driver.get(url)
    setNotification(driver, sl.get(0), sl.get(5), sl.get(6))
    submitAndClose(driver)
    
def closeMysql():
    if (conn):
        conn.close()
        
def main():
    connectMysql()
    if (conn == None):
        logger.error("Error: Fail to connect mysql")
        return 
        
    results = getCurDateResult()
    sendNotification(results)
    closeMysql()
    

if __name__ == "__main__":
    main()
    
    