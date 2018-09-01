# -*- coding: utf-8 -*-
import os
from flask_uploads import IMAGES

# 获取当前文件所在路径
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'app\static')
    UPLOADS_DEFAULT_ALLOW = IMAGES  # 限制上传类型
    FLASKY_MAIL_SUBJECT_PREFIX = '[Let\'s go]'
    FLASKY_MAIL_SENDER = '978772718@qq.com'
    FLASKY_ADMIN = '978772718@qq.com'

    CKEDITOR_SERVE_LOCAL = True   # #########################################
    CKEDITOR_HEIGHT = 600
    CKEDITOR_WIDTH = 800
    CKEDITOR_FILE_UPLOADER = 'main.upload'  # 设置图片上次的端口
    UPLOADED_PATH = os.path.join(basedir, 'app\static\\uploads')
    FLASKY_FOLLOWERS_PER_PAGE = 12

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # 每页显示4条游记数据
    FLASKY_POSTS_PER_PAGE = 4
    # 每页显示10条评论
    FLASKY_COMMETNS_PER_PAGE = 5
    # 搜索结果每页显示6条游记数据
    FLASKY_SEARCH_POSTS_PER_PAGE = 6
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = "978772718@qq.com"
    MAIL_PASSWORD = 'bkwthtfezfklbbje'  #POP3/SMTP服务
    # MAIL_PASSWORD = 'aezbbyftyqxsbfjh'  #IMAP/SMTP服务
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir,'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir,'data.sqlite')


config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,

    'default':DevelopmentConfig
}
