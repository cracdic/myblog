# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, request, flash, abort, \
                  current_app, jsonify
from flask_login import login_user, login_required, logout_user
from flask_sqlalchemy import get_debug_queries

from . import main
from .. import pictures
from .forms import LoginForm, PostForm
from ..models import User, Post, Tag


def subject_filter(subject):
    tags = Tag.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(subject=subject).order_by(
        Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    user = User.query.first()
    return (posts, pagination, tags, user)


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_DB_QUERY_TIMEOUT']:
            current_app.logger.warning(
                ('Slow query: %s\nParameters: %s\n'
                 'Duration: %fs\nContext: %s\n') %
                (query.statement, query.parameters, query.duration,
                 query.context))
    return response


@main.route('/Programming')
def pro_posts():
    post = subject_filter('programming')
    return render_template('index.html', posts=post[0],
                           pagination=post[1], tags=post[2],
                           user=post[3])


@main.route('/Animation')
def ani_posts():
    post = subject_filter(u'animation')
    return render_template('index.html', posts=post[0],
                           pagination=post[1], tags=post[2],
                           user=post[3])


@main.route('/Music')
def muse_posts():
    post = subject_filter(u'music')
    return render_template('index.html', posts=post[0],
                           pagination=post[1], tags=post[2],
                           user=post[3])


@main.route('/Tag/<name>')
def tag(name):
    tags = Tag.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.filter_by(name=name).first().posts.order_by(
        Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    user = User.query.first()
    return render_template('index.html', posts=posts,
                           pagination=pagination, tags=tags,
                           user=user)


@main.route('/')
def index():
    tags = Tag.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    user = User.query.first()
    return render_template('index.html', posts=posts, user=user,
                           pagination=pagination, tags=tags)


@main.route('/search', methods=['GET', 'POST'])
def w_search():
    tags = Tag.query.all()
    if request.method == "POST":
        keyword = request.values.get('keyword')
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.whoosh_search(
        keyword, limit=20).order_by(
        Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
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
        tags_new = [tag for tag in tags_new if tag not in ['', ' ', None]]
        Tag.insert_tags(tags_new)
        post = Post(subject=form.select.data,
                    body=form.body.data,
                    title=form.title.data)
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
        tags_new = [tag for tag in tags_new if tag not in ['', ' ', None]]
        Tag.insert_tags(tags_new)
        post.subject = form.select.data
        post.body = form.body.data
        post.title = form.title.data
        post.add_and_remove_tags(tags_old, tags_new)
        Tag.delete_tags(set(tags_old) - set(tags_new))
        flash(u'文章已更新')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    form.title.data = post.title
    return render_template('edit.html', form=form, tags=tags)


@main.route('/upload/', methods=['POST'])
@login_required
def upload_picture():
    if 'file' in request.files:
        filename = pictures.save(request.files['file'])
        # file_url = pictures.url(filename)
        # relative path
        file_url = current_app.config['RENDER_PICTURES_DEST'] + filename
        return jsonify({'name': filename,
                        'url': file_url,
                        'status': 'upload success'})
    return jsonify({'status': "upload fail"})


# get post and record this view
@main.route('/post/<id>')
def post(id):
    post = Post.query.get_or_404(id)
    if 'X-Real-IP' in request.headers:
        post.add_record(request.headers['X-Real-IP'])
    return render_template('post.html', post=post,
                           view_counts=post.ip_viewed.count(),
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


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'你已退出登录。')
    return redirect(url_for('main.index'))


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
