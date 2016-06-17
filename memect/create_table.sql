CREATE DATABASE `memect` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

use memect;

CREATE TABLE ml_memect ( 
    ml_id INT NOT NULL AUTO_INCREMENT,
    author_name VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    author_img_url VARCHAR(500),
    author_page_url VARCHAR(500),
    pub_time DATETIME,
    keywords VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_text VARCHAR(1500) CHARACTER SET utf8 COLLATE utf8_general_ci, 
    content_img_url VARCHAR(500),
    content_page_url VARCHAR(500),
    PRIMARY KEY(ml_id)
    );

CREATE TABLE py_memect ( 
    ml_id INT NOT NULL AUTO_INCREMENT,
    author_name VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    author_img_url VARCHAR(500),
    author_page_url VARCHAR(500),
    pub_time DATETIME,
    keywords VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_text VARCHAR(1500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_img_url VARCHAR(500),
    content_page_url VARCHAR(500),
    PRIMARY KEY(ml_id)
    );

CREATE TABLE web_memect ( 
    ml_id INT NOT NULL AUTO_INCREMENT,
    author_name VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    author_img_url VARCHAR(500),
    author_page_url VARCHAR(500),
    pub_time DATETIME,
    keywords VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_text VARCHAR(1500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_img_url VARCHAR(500),
    content_page_url VARCHAR(500),
    PRIMARY KEY(ml_id)
    );

CREATE TABLE app_memect ( 
    ml_id INT NOT NULL AUTO_INCREMENT,
    author_name VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    author_img_url VARCHAR(500),
    author_page_url VARCHAR(500),
    pub_time DATETIME,
    keywords VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_text VARCHAR(1500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_img_url VARCHAR(500),
    content_page_url VARCHAR(500),
    PRIMARY KEY(ml_id)
    );

CREATE TABLE bd_memect ( 
    ml_id INT NOT NULL AUTO_INCREMENT,
    author_name VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    author_img_url VARCHAR(500),
    author_page_url VARCHAR(500),
    pub_time DATETIME,
    keywords VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_text VARCHAR(1500) CHARACTER SET utf8 COLLATE utf8_general_ci,
    content_img_url VARCHAR(500),
    content_page_url VARCHAR(500),
    PRIMARY KEY(ml_id)
    );

CREATE TABLE sha1url ( 
    sha1 VARCHAR(50),
    url VARCHAR(500)
    );

