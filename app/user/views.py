# -*- coding: utf-8 -*-

from werkzeug import secure_filename
from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import current_user, login_required
from . import user
from .. import db, pictures
from .forms import UploadForm
from ..models import User, Post, Tag

@user.route('/user-profile/', methods=['GET', 'POST'])
@login_required
def profile():
    form = UploadForm()
    if request.method == 'POST' and 'avatar' in request.files:
        filename = pictures.save(request.files['avatar'])
        file_url = current_app.config['RENDER_PICTURES_DEST'] + filename
        current_user.avatar = file_url
        db.session.add(current_user)
        db.session.commit()
        flash(u'头像已更新')
        return redirect(url_for('.profile'))
    return render_template('user/profile.html', form=form)
