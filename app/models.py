# -*- coding: utf-8 -*-

from . import db
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.exceptions import ValidationError
from datetime import datetime
from markdown import markdown
from jieba.analyse import ChineseAnalyzer
import sys
import hashlib
import bleach

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError(u'密码不是可读属性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.id

categories = db.Table('categories',
    db.Column('post_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('posts.id')))

class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), default='')

    def __repr__(self):
        return '<Tag %r>' % self.id

    @property
    def tags_all(self):
        return [tag.name for tag in Tag.query.all()]

    @staticmethod
    def insert_tags(tags_input):
        tags_all = [tag.name for tag in Tag.query.all()]
        tags_insert = set(tags_input) - set(tags_all)
        for tag_insert in tags_insert:
            tag = Tag(name=tag_insert)
            db.session.add(tag)
        db.session.commit()

    @staticmethod
    def delete_tags(tags_delete):
        for tag_delete in tags_delete:
            tag = Tag.query.filter_by(name=tag_delete).first()
            if tag and not tag.posts.count():
                db.session.delete(tag)
        db.session.commit()

class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['subject', 'title', 'body']
    __analyzer__ = ChineseAnalyzer()

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.Text)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body_html = db.Column(db.Text)
    body_brief = db.Column(db.Text)
    tags = db.relationship('Tag',
                           secondary=categories,
                           backref=db.backref('posts', lazy='dynamic'),
                           lazy='dynamic')

    def __repr__(self):
        return '<Post %r>' % self.id

    def add_and_remove_tags(self, tags_old, tags_new):
        new = set(tags_new)
        old = set(tags_old)
        tags_remove = old - new
        tags_add = new - old
        for tag_add in tags_add:
            tag = Tag.query.filter_by(name=tag_add).first()
            if tag:
                self.tags.append(tag)
        for tag_remove in tags_remove:
            tag = Tag.query.filter_by(name=tag_remove).first()
            if tag:
                self.tags.remove(tag)
        db.session.add(self)
        db.session.commit()
        posts = Post.query.all()

    @property
    def tags_post(self):
        tag_objects = self.tags.all()
        tags = [tag_object.name for tag_object in tag_objects]
        return tags

    @staticmethod
    def on_changed_body_html(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {'img': ['alt', 'src']}
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=attrs, strip=True))

    @staticmethod
    def on_changed_body_brief(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        brief = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))
        target.body_brief = brief[0:600] + '...'

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(5, 10)),
                     timestamp=forgery_py.date.date(True))
            db.session.add(p)
            db.session.commit()


db.event.listen(Post.body, 'set', Post.on_changed_body_html)
db.event.listen(Post.body, 'set', Post.on_changed_body_brief)
