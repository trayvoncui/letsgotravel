# -*- coding:utf-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail   # 从app/__init__.py文件中导入


def send_async_email(app, msg):
    # with 确保不管使用过程中是否发生异常都会执行必要的“清理”操作，如文件使用后自动关闭
    with app.app_context():  # 让当前上下文current_app指向app,“app_context()”方法会创建一个”AppContext”类型对象，应用上下文对象
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()   # 获取当前app对象
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr