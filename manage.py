import os,sys
from app import create_app,db
from app.models import User,Role,Permission,Post,ArticleType
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand
from app.main.forms import icon,icon1
from flask_uploads import configure_uploads
# 启动脚本

import importlib
importlib.reload(sys)  #修改PYTHON默认字符编码


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)
configure_uploads(app, icon)  #再把app和这个icon这个上传组给绑定 ################
configure_uploads(app, icon1)



def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Permission=Permission,Post=Post,ArticleType=ArticleType)


manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)


if __name__ == '__main__':
    #app.run(debug=True)
    manager.run()