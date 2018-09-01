# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, request, make_response, send_from_directory, json
from flask import current_app,flash,abort
from flask_login import login_required,current_user

from . import main
from .. import db
from ..models import User, Role, Post,Comment,Permission
from .forms import CommentForm,icon,EditProfileForm,ImgForm,PostForm,icon1,SearchForm
from werkzeug.utils import secure_filename
import time
from flask_ckeditor import upload_fail, upload_success #########3
import os


@main.route('/')
def index():
    # 获取cookies值，根据点击设置的cookies,来判断进入哪一个类别
    show_food = bool(request.cookies.get('show_food',''))
    show_alone = bool(request.cookies.get('show_alone', ''))
    show_short = bool(request.cookies.get('show_short', ''))
    show_long = bool(request.cookies.get('show_long', ''))
    # 如果是第一次进来，且cookie都是False，session为0，默认选中show_food
    # time = session.get('time')
    if not show_food and not show_alone and not show_short and not show_long:
        show_food = True
    # if not time:
    #     if not show_food and not show_alone and not show_short and not show_long:
    #         show_food = True
    # 第一次进来之后的session都是1
    # session['time'] = '1'
    page = request.args.get('page',1,type=int)
    # 查询吃遍天下的游记
    if show_food:
        pagination = Post.query.filter_by(type_id=0).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
        # posts = Post.query.filter_by(type_id=0).all()
    # 查询独自一人的游记
    if show_alone:
        pagination = Post.query.filter_by(type_id=1).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
        # posts = Post.query.filter_by(type_id=1).all()
    # 查询短途周末的游记
    if show_short:
        pagination = Post.query.filter_by(type_id=2).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
        # posts = Post.query.filter_by(type_id=2).all()
    # 查询长途旅行的游记
    if show_long:
        pagination = Post.query.filter_by(type_id=3).order_by(Post.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        posts = pagination.items
        # posts = Post.query.filter_by(type_id=3).all()
    return render_template('index.html',posts=posts,show_food=show_food,show_alone=show_alone,
                           show_short=show_short,show_long=show_long,pagination=pagination)


@main.route('/show_food')
def show_food():
    resp = make_response(redirect(url_for('.index')))
    # 设置cookie值
    resp.set_cookie('show_food','1',max_age=30*24*60*60)
    resp.set_cookie('show_alone','',max_age=30*24*60*60)
    resp.set_cookie('show_short','',max_age=30*24*60*60)
    resp.set_cookie('show_long','',max_age=30*24*60*60)
    return resp


@main.route('/show_alone')
def show_alone():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_food','',max_age=30*24*60*60)
    resp.set_cookie('show_alone','1',max_age=30*24*60*60)
    resp.set_cookie('show_short','',max_age=30*24*60*60)
    resp.set_cookie('show_long','',max_age=30*24*60*60)
    return resp


@main.route('/show_short')
def show_short():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_food','',max_age=30*24*60*60)
    resp.set_cookie('show_alone','',max_age=30*24*60*60)
    resp.set_cookie('show_short','1',max_age=30*24*60*60)
    resp.set_cookie('show_long','',max_age=30*24*60*60)
    return resp


@main.route('/show_long')
def show_long():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_food','',max_age=30*24*60*60)
    resp.set_cookie('show_alone','',max_age=30*24*60*60)
    resp.set_cookie('show_short','',max_age=30*24*60*60)
    resp.set_cookie('show_long','1',max_age=30*24*60*60)
    return resp


# 查看文章详情
@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('评论成功！')
        return redirect(url_for('.post',id=post.id,page=-1))
    page = request.args.get('page',1,type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMETNS_PER_PAGE']+1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,per_page=current_app.config['FLASKY_COMMETNS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html',posts=[post],form=form,
                           comments=comments,pagination=pagination)


# 搜索
@main.route('/search',methods=['GET','POST'])
def search():
    searchCity = request.form['searchCity']  #获取id为searchCity的输入框的值
    cityname = Post.query.filter_by(city=searchCity).first()   #过滤出数据库中匹配的数据
    if cityname is None:
        return render_template('nocity.html',city=searchCity)
    session['city'] = searchCity
    page = request.args.get('page',1,type=int)
    pagination = Post.query.filter_by(city=searchCity).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_SEARCH_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('searchPosts.html',posts=posts,pagination=pagination)


# 搜索第二页
@main.route('/searchResult')
def searchResult():
    searchCity = session.get('city')
    page = request.args.get('page',1,type=int)
    pagination = Post.query.filter_by(city=searchCity).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_SEARCH_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('searchPosts.html',posts=posts,pagination=pagination)


# 修改个人资料  #######################################
@main.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items  # 通过posts访问到Post表

    flag = 1
    form1 = EditProfileForm(user=current_user)
    form_o = ImgForm()
    if form1.submit1.data and form1.validate_on_submit():
        flag = 2
        current_user.username = form1.username.data
        current_user.name = form1.name.data
        current_user.location = form1.location.data
        current_user.about_me = form1.about_me.data
        db.session.add(current_user)
        flash('保存成功')
        return render_template('setting.html', form1=form1, form_o=form_o, user=current_user,
                               flag=flag, posts=posts, pagination=pagination)
    if form_o.submit2.data and form_o.validate_on_submit():
        flag = 3
        tim = str(int(time.time()))
        if form_o.image.data is not None:  ##########################
            img = secure_filename(form_o.image.data.filename)
            fileurl = icon.save(form_o.image.data, name=tim+'.'+img)
            imgurl= url_for('static', filename='photo/' + fileurl, _external=True)
            current_user.avatar_hash = imgurl
            db.session.add(current_user)
            flash('图片上传成功')
        return render_template('setting.html', form1=form1, form_o=form_o, user=current_user,
                               flag=flag, posts=posts, pagination=pagination)
    form1.username.data = current_user.username
    form1.name.data = current_user.name
    form1.location.data = current_user.location
    form1.about_me.data = current_user.about_me
    return render_template('setting.html', form1=form1, form_o=form_o, user=current_user,
                           flag=flag, posts=posts, pagination=pagination)


# 写游记 #######################################################
@main.route('/edit_post', methods=['GET', 'POST'])
@login_required
def edit_post():
    form = PostForm()
    tim = str(int(time.time()))
    imgurl = None
    if form.validate_on_submit() and current_user.can(Permission.WRITE):
        if form.headimg.data is not None:
            img = secure_filename(form.headimg.data.filename)
            fileurl = icon1.save(form.headimg.data, name=tim+'.'+img)
            imgurl= url_for('static', filename='headimg/' + fileurl, _external=True)
        post = Post(title=form.title.data, city=form.city.data, headimg=imgurl,
                    body=form.body.data, type_id=form.type.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        flash('您的游记已保存')
        return redirect(url_for('.index'))
    return render_template('edit_post.html', form=form, flag=None)


# 来获取图片文件
@main.route('/files/<filename>')
def uploaded_files(filename):
    path = current_app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


# 处理并保存上传文件
@main.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')   # 获取上传文件对象
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='只能上传图片(图片格式jpg, gif,png,jpeg)!')
    f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))
    url = url_for('main.uploaded_files', filename=f.filename)
    return upload_success(url=url)


# 用户资料显示
@main.route('/user/<username>')
def user(username):
    # 使用 first_or_404() 来代替 first()。这样会抛出一个 404 错误，而不是返回 None: 不存在这个用户就404错误
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=3,
        error_out=False)
    posts = pagination.items   # 通过posts访问到Post表
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


# 重新编辑
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    tim = str(int(time.time()))
    imgurl = None
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.headimg.data is not None:
            img = secure_filename(form.headimg.data.filename)
            fileurl = icon1.save(form.headimg.data, name=tim+'.'+img)
            imgurl= url_for('static', filename='headimg/' + fileurl, _external=True)
        post.title = form.title.data
        post.city = form.city.data
        post.type_id = form.type.data
        post.body = form.body.data
        if imgurl is not None:
            post.headimg = imgurl
        db.session.add(post)
        db.session.commit()
        flash('您的游记已更新')
        return redirect(url_for('.post', id=post.id))
    form.type.data = post.type_id
    form.body.data = post.body
    form.title.data = post.title
    form.city.data = post.city
    flag = post.headimg
    return render_template('edit_post.html', form=form, flag=flag)


# 删除游记
@main.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    db.session.delete(post)
    db.session.commit()

    flash("删除成功")
    if current_user.is_administrator():
        return redirect(url_for('.index'))
    else:
        return redirect(url_for('.setting'))


# 关注
@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不是合法用户.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('您已经关注了这个用户。')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('您关注了%s。' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不是合法用户。')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('您并没有关注这个用户。')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('您不再关注%s' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="的粉丝",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="的关注",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


# 在自己关注中的人中取消关注
@main.route('/unfollow_in/<username>')
@login_required
def unfollow_in(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    current_user.unfollow(user)
    db.session.commit()
    flash('您不再关注 %s 。' % username)
    return redirect (url_for('.followed_by', username=current_user.username))


# 在粉丝中添加关注
@main.route('/follow_in/<username>')
@login_required
def follow_in(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('您已经关注了该用户。')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('您关注了 %s。' % username)
    return redirect (url_for('.followers', username=current_user.username))


@main.route('/moderate/enable/<int:id>')
@login_required
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.post',id=post_id))


@main.route('/moderate/disable/<int:id>')
@login_required
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.post', id=post_id))
