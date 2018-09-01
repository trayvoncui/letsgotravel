from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_mail import Mail
from flask_login import LoginManager
from flask_ckeditor import CKEditor

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
mail = Mail()   ################################################
login_manager = LoginManager()
login_manager.session_protection = 'strong'   # 可以设置None,'basic','strong'以提供不同的安全等级
login_manager.login_view = 'auth.login'       # 这里填写登陆界面的路由  ################################
ckeditor = CKEditor()  ################################


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)         ######################################################3
    login_manager.init_app(app)    ##############################################
    ckeditor.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint  ################################################
    app.register_blueprint(auth_blueprint, url_prefix='/auth')  # 注册蓝本

    return app
