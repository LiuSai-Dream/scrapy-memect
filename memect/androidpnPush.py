# -*- coding: utf-8 -*-
"""
Created on Sun Jul 03 00:27:13 2016

@author: user
"""

from settings import MySqlConfig
from datetime import datetime, timedelta
from selenium import webdriver
import logging
import MySQLdb
import gc
import random

logger = logging.getLogger(__name__)

class Notification():
    
    def __init__(self):
       self.url = "http://127.0.0.1:8080/notification.do"
       self.driver = None

    def setNotification(self, titleText, messageText, uriText):
        logger.debug("title : "+ titleText)    
        logger.debug("message : "+ messageText)        
        logger.debug("uri : "+ uriText) 
        
        title = self.driver.find_element_by_name("title")
        title.clear()
        title.send_keys(str(titleText).decode("utf8"))
        
        message = self.driver.find_element_by_name("message")
        message.clear()
        message.send_keys(str(messageText).decode("utf8"))
        
        uri = self.driver.find_element_by_name("uri")
        uri.clear()
        uri.send_keys(uriText)
        

    def send(self):
        submit = self.driver.find_element_by_xpath("//input[contains(@type,'submit')]")
        submit.submit()
        self.driver.close()
        
    def sendNotification(self, results):
        sl = None
        if (len(results) <= 0):
            sl = safeList([])
        else:
            index = random.randint(0, len(results))
            sl = safeList(results[index])        
        
        # Trigger an request
        self.driver = webdriver.PhantomJS('phantomjs')
        self.driver.get(self.url)
        
        self.setNotification(sl.get(0), sl.get(5), sl.get(6))
        self.send()


class safeList(list):
    def get(self, index, default="No Value"):
        try:
            return self.__getitem__(index)
        except IndexError:            
            return default
        
class MemectMysql():

    def __init__(self):
        self.user = MySqlConfig['user'],
        self.passwd = MySqlConfig['passwd'],
        self.dbname = MySqlConfig['db'],
        self.host = MySqlConfig['host'],
        self.charset = "utf8",
        self.use_unicode = True
        self.conn = None
        self.cur = None
        self.curDate = datetime.now().date().strftime("%Y-%m-%d") - timedelta(3)()
        
    def connect(self):
        try:
            # Exceptions make it extremely difficult to clean up bu hand.
            # Manually invok python garbage collector 
            # which close off any old Mysql connections
            gc.collect()        
            
            # Connect to mysql database
            self.conn = MySQLdb.connect(user = self.user, passwd = self.passwd, db = self.dbname, host = self.host , charset = self.charset, use_unicode = self.use_unicode)
    		
            # All operations are performed in the cursor
            self.cur = conn.cursor()
            logger.debug('Debug: Connecting to database successfully')
        except :
            if (self.conn):
                self.conn.close()  
            raise Exception

    def query(self):
        query = """SELECT ( author_name, author_img_url, author_page_url, pub_time, keywords, content_text, content_page_url,  content_img_url) FROM (%s) WHERE pub_time LIKE (%s) """    
        tables = ["ml_memct", "bd_memect", "app_memect", "web_memect", "py_memect"]
        results = []
            
        for table in tables:
            resultNum = cur.execute(query, (table, self.curDate))
            if (resultNum != 0):
                result = self.cur.fetchAll()
                print(result)
        else:
            logger.warn("Warning: No data in table " + table)
        return results
    
    def close(self):
        if (self.conn):
            self.conn.close()
    

        
def main():
    mm = MemectMysql()  
    try:    
        mm.connect()
        results = mm.query() 
    except Exxception:
        logger.error("Error: Fail to connect mysql!")
        return
    finally:
        mm.close()        
            
    notification = Notification()
    notification.sendNotification(results)
    

if __name__ == "__main__":
    main()
    
    