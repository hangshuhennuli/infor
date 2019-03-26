from flask import Flask
from info.shop.index import index_blue
from flask_script import Manager
from models import *
from info.admin.admin import admin_blue

#迁移
from flask_migrate import Migrate,MigrateCommand
from apps import app,db

manage = Manager(app)
migrate = Migrate(app,db)
manage.add_command('db',MigrateCommand)
#注册前台蓝图
app.register_blueprint(index_blue)
# 注册后台蓝图
app.register_blueprint(admin_blue,url_prefix="/admin")

if __name__ == "__main__":
    # manage.run()
    app.run()