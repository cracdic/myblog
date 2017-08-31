# -*- coding: utf-8 -*-

import pdb
import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db
from app.models import User, Post, Tag

class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # start Chrome
        try:
            cls.client = webdriver.Chrome()
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # create the database and insert some posts
            db.create_all()
            p1 = Post(title='programming title',
                      body='programming body',
                      subject='programming')
            p2 = Post(title='animation title',
                      body='animation body',
                      subject='animation')
            p3 = Post(title='music title',
                      body='music body',
                      subject='music')
            db.session.add_all([p1, p2, p3])

            # add an user
            u = User(email='test@ex.com',
                     password='cat')
            db.session.add(u)
            db.session.commit()

            # start the Flask server in a thread
            threading.Thread(target=cls.app.run).start()

            # give the server a second to ensure it is up
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application context
            cls.app_context.pop()
            
    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def login(self, email, password):
        self.client.get('http://localhost:5000/admin-login')
        self.client.find_element_by_name('email').send_keys(email)
        self.client.find_element_by_name('password').send_keys(password)
        self.client.find_element_by_name('submit').click()

    def test_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('programming title',
                                  self.client.page_source))
        self.assertTrue(re.search('programming body',
                                  self.client.page_source))
        self.assertTrue(re.search('animation title',
                                  self.client.page_source))
        self.assertTrue(re.search('animation body',
                                  self.client.page_source))
        self.assertTrue(re.search('music title',
                                  self.client.page_source))
        self.assertTrue(re.search('music body',
                                  self.client.page_source))

    def test_login_logout(self):
        self.login('test@ex.com', 'cat')
        self.assertTrue(re.search('Settings',
                                  self.client.page_source))
        self.assertTrue(re.search(u'编辑',
                                  self.client.page_source))
        self.client.find_element_by_name('logout').click()
        self.client.get('http://localhost:5000/newpost')
        self.assertTrue(re.search(u'登录',
                                  self.client.page_source))

    def test_subjects(self):
        self.client.get('http://localhost:5000/')
        self.client.find_element_by_link_text(u'编程').click()
        self.assertTrue(re.search('programming title',
                                  self.client.page_source))
        self.assertTrue(re.search('programming body',
                                  self.client.page_source))
        self.client.find_element_by_link_text(u'动画').click()
        self.assertTrue(re.search('animation title',
                                  self.client.page_source))
        self.assertTrue(re.search('animation body',
                                  self.client.page_source))
        self.client.find_element_by_link_text(u'音乐').click()
        self.assertTrue(re.search('music title',
                                  self.client.page_source))
        self.assertTrue(re.search('music body',
                                  self.client.page_source))

    def test_newpost(self):
        self.login('test@ex.com', 'cat')
        self.client.get('http://localhost:5000/newpost')
        self.assertTrue(re.search(u'编辑文章',
                                  self.client.page_source))
        self.client.find_element_by_name('title').send_keys('test title')
        self.client.find_element_by_name('body').send_keys('test body')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search(u'已发布新文章',
                                  self.client.page_source))
        self.client.find_element_by_name('logout').click()
        self.assertTrue(re.search('test title', 
                                  self.client.page_source))
        self.assertTrue(re.search('test body',
                                  self.client.page_source))

    def test_tags(self):
        self.login('test@ex.com', 'cat')
        p = Post(title='test3 title',
                 body='test3 body')
        tag = Tag(name='this')
        db.session.add(tag)
        p.tags.append(tag)
        db.session.add(p)
        db.session.commit()
        self.client.get('http://localhost:5000/')
        self.client.find_element_by_link_text('this(1)').click()
        self.assertTrue(re.search('test3 title',
                                  self.client.page_source))

    def test_search(self):
        self.client.get('http://localhost:5000/')
        self.client.find_element_by_name('keyword').clear()
        self.client.find_element_by_name('keyword').send_keys('music')
        self.client.find_element_by_name('search-btn').click()
        self.assertTrue(re.search('music title',
                                  self.client.page_source))
        self.assertTrue(re.search('music body',
                                  self.client.page_source))
        self.assertFalse(re.search('animation title',
                                   self.client.page_source))
        self.assertFalse(re.search('programming title',
                                   self.client.page_source))

    def test_edit(self):
        self.login('test@ex.com', 'cat')
        p = Post(title='edit title',
                 body='edit body')
        db.session.add(p)
        db.session.commit()
        self.client.get('http://localhost:5000/edit/' + str(p.id))
        self.client.find_element_by_name('title').clear()
        self.client.find_element_by_name('title').send_keys('edited title')
        self.client.find_element_by_name('body').clear()
        self.client.find_element_by_name('body').send_keys('edited body')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search(u'文章已更新',
                                  self.client.page_source))
        self.assertTrue(re.search('edited title',
                                  self.client.page_source))
        self.assertTrue(re.search('edited body',
                                  self.client.page_source))
        self.client.find_element_by_name('logout').click()

