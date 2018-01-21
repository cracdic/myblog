# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_pagedown.fields import PageDownField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from .. import pictures

class LoginForm(FlaskForm):
    email = StringField(u'你的邮箱', validators=[
        Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'保持登录')
    submit = SubmitField(u'登录')


class PostForm(FlaskForm):
    title = StringField(u'标题', validators=[
        Required(), Length(1, 64)])
    select = SelectField(u'分类', choices=[('programming', u'编程'),
                                                   ('animation', u'动画'),
                                                   ('music', u'音乐')])
    body = PageDownField(u'输入markdown文本', validators=[Required()])
    submit = SubmitField(u'提交')
