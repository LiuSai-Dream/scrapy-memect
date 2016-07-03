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

logging.basicConfig(filename="androidpn.log", level=logging.DEBUG)
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
            logger.warn("All results is 0")
            sl = safeList([])
        else:
            index = random.randint(0, len(results))
            sl = safeList(results[index])        
        
        # Trigger an request
        self.driver = webdriver.PhantomJS('phantomjs')
        self.driver.get(self.url)
        
        self.setNotification(str(sl.get(1)), str(sl.get(6)), str(sl.get(7)))
        self.send()


class safeList(list):
    def get(self, index, default="No Value"):
        try:
            return self.__getitem__(index)
        except IndexError:            
            return default
        
class MemectMysql():

    def __init__(self):
        self.user = MySqlConfig['user']
        self.passwd = MySqlConfig['passwd']
        self.dbname = MySqlConfig['db']
        self.host = MySqlConfig['host']
        self.charset = "utf8"
        self.use_unicode = True
        self.conn = None
        self.cur = None
        self.curDate = (datetime.now().date() - timedelta(2)).strftime("%Y-%m-%d")
        
    def connect(self):

        try:
            # Exceptions make it extremely difficult to clean up bu hand.
            # Manually invok python garbage collector 
            # which close off any old Mysql connections
            gc.collect()        
            
            # Connect to mysql database
            self.conn = MySQLdb.connect(user = self.user, passwd = self.passwd, db = self.dbname, host = self.host , charset = self.charset, use_unicode = self.use_unicode)
    		
            # All operations are performed in the cursor
            self.cur = self.conn.cursor()
            logger.debug('Connecting to database successfully')
        except :
            if (self.conn):
                self.conn.close()  
            raise Exception

    def query(self):
        tables = ["ml_memect", "bd_memect", "app_memect", "web_memect", "py_memect"]
        results = []
        
        try:
            for table in tables:
                query = "SELECT * FROM " + table + " WHERE pub_time LIKE '" + self.curDate + "%'"

                resultNum = self.cur.execute(query)
                if (resultNum != 0):
                    result = self.cur.fetchall()
                    results.append(list(result))
                    print("Result is " + str(list(result)))
                else:
                    logger.warn("No data in table " + table)
        except MySQLdb.Error as e:
            logger.error("Fail to query; " + str(e))
        except Exception as e:
            logger.error("Other " + str(e))
        return results
    
    def close(self):
        if (self.conn):
            self.conn.close()
    

        
def main():
    mm = MemectMysql()
    try:    
        mm.connect()
        results = mm.query() 
    except Exception:
        logger.error("Fail to connect or query")
        return
    finally:
        mm.close()        
            
    notification = Notification()
    notification.sendNotification(results)
    

if __name__ == "__main__":
    main()
    
    