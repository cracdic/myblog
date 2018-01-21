# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from .. import pictures

class UploadForm(FlaskForm):
    avatar = FileField(u'头像上传', validators=[
        FileAllowed(pictures, u'只能上传图片！'),
        FileRequired(u'未选择文件！')])
    submit = SubmitField(u'上传')
