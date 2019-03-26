from apps import db
from datetime import datetime
#基础表
class BaseModel(object):
    create_time = db.Column(db.DateTime,default=datetime.now)
    update_time = db.Column(db.DateTime,default=datetime.now)

#分类表
class Cate(BaseModel,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30))

#产品表
class Goods(BaseModel,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30))
    price = db.Column(db.Integer)
    descrip = db.Column(db.String(255)) #描述信息
    content = db.Column(db.Text) #内容
    image_url=db.Column(db.String(100))
    number =db.Column(db.Integer) #库存
    cid = db.Column(db.Integer,db.ForeignKey('cate.id'))
    cate = db.relationship(Cate)
# 用户表
class User(BaseModel,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30))
    password = db.Column(db.String(255))
# 购物车表
class Cart(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    good_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(30),default='')
    price = db.Column(db.Integer)
    number = db.Column(db.Integer)
    
#评论表
class Comment(BaseModel,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(30))
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    good_id = db.Column(db.Integer,db.ForeignKey("goods.id"))
    like_count = db.Column(db.Integer,default=0)
    user = db.relationship(User)
  

# 5.创建迁移仓库
#  #这个命令会创建migrations文件夹，所有迁移文件都放在里面。
# python manage.py db init


# 6.创建迁移脚本
# python manage.py db migrate -m 'ini
# ation'

# 7.更新数据库
# python manage.py db upgrade