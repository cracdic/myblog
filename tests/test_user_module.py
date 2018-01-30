# -*- coding -*- utf-8 -*-

import unittest
from datetime import datetime
from app import create_app, db
from app.models import User, Post, Tag, IpAddress


class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_post_timestamp(self):
        p = Post(body='this is a test')
        db.session.add(p)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - p.timestamp).total_seconds() < 3)

    def test_post_html_filter(self):
        p1 = Post(body='<img src="" alt="">')
        p2 = Post(body='<a></a>')
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        self.assertTrue('<a></a>' in p2.body_html)
        self.assertTrue('<a></a>' in p2.body_brief)
        self.assertTrue('<img src="" alt="">' in p1.body_html)
        self.assertTrue('<img src="" alt="">' not in p1.body_brief)

    def test_add_and_remove_tags(self):
        p = Post(body='test')
        t1 = Tag(name='flask')
        t2 = Tag(name='test')
        t3 = Tag(name='tags')
        db.session.add_all([p, t1, t2, t3])
        db.session.commit()
        p.add_and_remove_tags([], ['flask', 'test', 'tags'])
        post_tags = p.tags_post
        self.assertTrue('flask' in post_tags)
        self.assertTrue('test' in post_tags)
        self.assertTrue('tags' in post_tags)
        p.add_and_remove_tags(['flask', 'test', 'tags'], [])
        post_tags = p.tags_post
        self.assertFalse('flask' in post_tags)
        self.assertFalse('test' in post_tags)
        self.assertFalse('tags' in post_tags)

    def test_insert_and_delete_tags(self):
        tags_input = ['flask', 'test', 'tags']
        Tag.insert_tags(tags_input)
        tags = Tag().tags_all
        self.assertTrue('flask' in tags)
        self.assertTrue('test' in tags)
        self.assertTrue('tags' in tags)
        Tag.delete_tags(tags_input)
        self.assertTrue(Tag().tags_all == [])

    def test_append_and_remove_ip(self):
        p = Post(title='testt', body='testp')
        db.session.add(p)
        db.session.commit()
        self.assertTrue(p.ip_viewed.count() == 0)
        ip1 = IpAddress(ipaddr=IpAddress.ip2int("213.213.123.21"))
        ip2 = IpAddress(ipaddr=IpAddress.ip2int("111.222.121.4"))
        p.ip_viewed.append(ip1)
        db.session.add_all([ip1, p])
        db.session.commit()
        self.assertTrue(p.ip_viewed.count() == 1)
        ip1_select = IpAddress.query.filter_by(
                         ipaddr=IpAddress.ip2int("213.213.123.21"))
        self.assertTrue(ip1_select is not None)
        p.ip_viewed.append(ip2)
        db.session.add_all([ip2, p])
        db.session.commit()
        self.assertTrue(p.ip_viewed.count() == 2)
        p.ip_viewed.remove(ip1)
        db.session.add(p)
        db.session.commit()
        self.assertTrue(p.ip_viewed.count() == 1)
