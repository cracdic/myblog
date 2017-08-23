# -*- coding: utf-8 -*-

from datetime import datetime
from pprint import pprint
from flask import render_template, session, redirect, url_for, request, flash, current_app, \
    jsonify
from flask_login import current_user, login_user, login_required

from . import main
from .. import db, pictures
from .forms import LoginForm, PostForm, UploadForm
from ..models import User, Post, Tag

def subject_filter(subject):
    tags = Tag.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(subject=subject).order_by(
        Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return (posts, pagination, tags)

@main.route('/Programming')
def pro_posts():
    post = subject_filter(u'编程')
    return render_template('index.html', posts=post[0],
                           pagination=post[1], tags=post[2])

@main.route('/Animation')
def ani_posts():
    post = subject_filter(u'动画')
    return render_template('index.html', posts=post[0],
                           pagination=post[1], tags=post[2])

@main.route('/Music')
def muse_posts():
    post = subject_filter(u'音乐')
    return render_template('index.html', posts=post[0],
                           pagination=post[1], tags=post[2])

@main.route('/Tag/<name>')
def tag(name): 
    tags = Tag.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.filter_by(name=name).first().posts.order_by(
        Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts,
                           pagination=pagination, tags=tags)

@main.route('/')
def index():
    tags = Tag.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts,
                           pagination=pagination, tags=tags)

@main.route('/newpost', methods=['GET', 'POST'])
@login_required
def new():
    form = PostForm()
    tags_all = Tag().tags_all
    if form.validate_on_submit():
        tags_new = [x.strip() for x in request.form.get('tags').split(',')]
        Tag.insert_tags(tags_new)
        post = Post(body=form.body.data, title=form.title.data)
        post.add_and_remove_tags([], tags_new)
        flash(u'已发布新文章')
        return redirect(url_for('.post', id=post.id))
    return render_template('edit.html', form=form, tags=','.join(tags_all))

@main.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    tags_old = post.tags_post
    tags = ','.join(tags_old)
    if form.validate_on_submit():
        tags_new = [x.strip() for x in request.form.get('tags').split(',')]
        Tag.insert_tags(tags_new)
        post.add_and_remove_tags(tags_old, tags_new)
        Tag.delete_tags(tags_old, tags_new)
        post.body = form.body.data
        post.title = form.title.data
        db.session.add(post)
        db.session.commit()
        flash(u'文章已更新')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    form.title.data = post.title
    return render_template('edit.html', form=form, tags=tags)

@main.route('/upload', methods=['POST'])
@login_required
def upload_picture():
    if 'file' in request.files:
        filename = pictures.save(request.files['file'])
        file_url = pictures.url(filename)
        return jsonify({'name': filename,
                        'url': file_url,
                        'status': 'upload success'})
    return jsonify({'status': "upload fail"})

@main.route('/post/<id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post,
                           tags=post.tags.all())


@main.route('/admin-login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        if user is None or not user.verify_password(form.password.data):
            flash(u'用户名或密码错误')
    return render_template('login.html', form=form)
