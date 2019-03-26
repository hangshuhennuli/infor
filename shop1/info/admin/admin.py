from flask import Blueprint,request,render_template,redirect,url_for,session,flash,jsonify,g
from models import *
from apps import photos
import re
from utils.comm import isLogin
from utils.constant import admin_news_count
admin_blue = Blueprint('admin',__name__)


# 详情页
@admin_blue.route("/cates")
def cates():
    current_page = request.args.get('p',1)
    #搜索 获取搜索值
    keyword = request.args.get('keyword')
    page_count=2
    #分页
    if keyword:
        cate = Cate.query.filter(Cate.name.like('%'+keyword+'%')).paginate(int(current_page),page_count,False)
    else:
        keyword = ''
        cate = Cate.query.paginate(int(current_page),page_count,False)
    data = {'cate':cate.items,'current_page':cate.page,'total_page':cate.pages,'keyword':keyword}
    return render_template('admin/cates.html',data=data)

# 添加数据
@admin_blue.route("/goods",methods=['get','post'])
def goods():
    if request.method == "POST":
        name = request.form.get('name')
        price = request.form.get('price')
        descrip = request.form.get('descrip')
        content = request.form.get('content')
        number = request.form.get('number')
        index_image = request.files['index_image']
        image_data = photos.save(index_image)  # 保存图片到本地和返回图片名字
        image_url = 'static/upload/'+image_data
        cid = request.form.get('cid')
        if not image_data:
            flash('图片上传不成功')
        goods = Goods(name=name,price=price,descrip=descrip,content=content,number=number,image_url=image_url,cid=cid)
        try:
            db.session.add(goods)
            db.session.commit()
            flash('添加成功')
        except Exception as e:
            flash('没有添加成功')
    cates = Cate.query.all()
    return render_template("admin/goods.html",cates=cates)

# 添加分类
@admin_blue.route('/add_cate',methods=['get','post'])
def add_cate():
    if request.method=='POST':
        name= request.form.get('name')
        new_cate = Cate(name=name)
        try:
            db.session.add(new_cate)
            db.session.commit()
            flash('添加分类成功')
        except Exception as  e:
            flash('没有添加分类成功')
    return render_template('admin/add_cate.html')
    
