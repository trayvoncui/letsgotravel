# -*- coding:utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from . import auth
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,  \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from .. import db
from ..email import send_email


@auth.before_app_request   # 在所有请求之前调用该函数
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint \
                  and request.blueprint != 'auth' \
                  and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))
# (1) 用户已登录（current_user.is_authenticated() 必须返回True）。
# (2) 用户的账户还未确认。
# (3) 请求的端点（使用request.endpoint 获取）不在认证蓝本中。访问认证路由要获取权
# 限，因为这些路由的作用是让用户确认账户或执行其他账户管理操作。


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)   # 把用户标记为已登陆，并选择是否要记住此用户
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误')
    return render_template('auth/login.html', form=form)


# @login_required
# 如果用户没有登陆而直接访问就会跳转到登陆界面，
# 用户在跳转的登陆界面中完成登陆后，自动访问跳转到之前访问的地址
@auth.route('/logout')
@login_required
def logout():
    logout_user()   # 删除并重设用户会话
    flash('您已退出登录！')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])  # methods !!!! s!!!
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()   # 调用函数生成令牌
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm',
                   user=user, token=token)   ############
        flash('确认邮件已经发送到您的邮箱，请前往邮箱确认！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):   # 调用User模型中的confirm函数进行验证
        flash('You have confirmed your account. Thanks!')
    else:
        flash('确认链接无效或已过期！')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))  # (is_anonymous对普通用户返回False)，或者已确认的，则返回主页
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your account', 'auth/email/confirm', user=current_user, token=token)
    flash('确认邮件已经发送到您的邮箱，请前往邮箱确认！')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):  # 老密码的认证返回True
            current_user.password = form.password.data
            db.session.add(current_user)    # 更新模型
            db.session.commit()
            flash('密码修改成功！')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:    # ????
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password', user=user,
                       token=token, next=request.args.get('next'))
        flash('重置密码确认邮件已经发送到您的邮箱，请前往邮箱确认')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('密码重置成功！')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):  # 验证密码
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)

            flash('修改邮箱确认邮件已经发送到您的邮箱，请前往邮箱确认')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):   # 验证token
        db.session.commit()
        flash('邮箱修改成功！')
    else:
        flash('邮箱修改失败，请重试')
    return redirect(url_for('main.index'))
