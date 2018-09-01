# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                        Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('一直处于登录状态')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名',validators=[DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'username must have only letters,numbers, dots or underscores')])
    # 可以匹配由字母开头，后接任意个由一个数字、字母、下划线或者点组成的字符串

    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('立即注册')

    def validate_email(self, field):  # 以validate_开头的函数，会和普通验证函数一起被调用
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in user.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('修改密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='Password must match')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('重置密码')


class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64),
                                                 Email()])  # 验证邮箱
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('修改邮箱')

    def validate_email(self, field):    # 确保邮箱的唯一性
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')
