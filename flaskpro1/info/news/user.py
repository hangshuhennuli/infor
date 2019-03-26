from flask import Blueprint,render_template,session,g,make_response,request,jsonify,redirect,url_for
from utils.captcha.captcha import captcha
from models import *
from werkzeug.security import generate_password_hash,check_password_hash 
import re
from datetime import datetime
from utils.comm import isLogin
from apps import photos
from utils.constant import admin_news_count
user_blue = Blueprint('user',__name__)

@user_blue.route("/get_image")
def get_image():
    name,text,image_url = captcha.generate_captcha()
    session['image_code'] = text
    response = make_response(image_url)
    response.headers['Content-type'] = "image/jpg"
    return response

@user_blue.route("/register",methods=['post'])
def register():
    mes = {}
    mobile = request.form.get('mobile',0)
    password = request.form.get('password','')
    sms_code = request.form.get('sms_code','')
    try:
        agree = int(request.form.get('agree',''))
    except:
        agree = 2
    if not all([mobile,password,sms_code,agree]):
        mes['code'] = 10013
        mes['message'] = '参数不完整'
    else:
        #是否同意协议
        if agree == 1:
            #判断图片验证码是否正确
            imagecode = session.get('image_code')
            if imagecode.upper() != sms_code.upper():
                mes['code'] = 12001
                mes['message'] = '验证码错误'
            else:
                password = generate_password_hash(password)
                user = User(nick_name=mobile,password_hash=password,mobile=mobile)
            try:
                db.session.add(user)
                session['username'] = mobile
                mes['code'] = 200
                mes['message'] = "成功"
            except:
                mes['code'] = '250250'
                mes['message'] = '此号已被注册'
        else:
            mes['code'] = 120012
            mes['message'] = '未勾选协议'
    return jsonify(mes)
#登录
@user_blue.route("/login",methods=['post','get'])
def login():
    mes = {}
    if request.method == "POST":
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        if not all([mobile,password]):
            mes['code'] = 138138
            mes['message'] = '用户名密码不能为空'
        else:
            #用户名必须是数字，字母，下划线和5到8位
            flag = re.match("^1[3,8,5]\d{9}$",mobile)
            if flag == False:
                mes['code'] = 138147
                mes['message'] = '用户名格式错误'
            else:
                user = User.query.filter(User.mobile==mobile).first()
                if not user:
                    mes['code'] = 138456
                    mes['message'] = '用户不存在'
                else:
                    flag = check_password_hash(user.password_hash,password)
                    if flag:
                        session['username'] = mobile
                        session['user_id'] = user.id
                        mes['code'] = 200
                        mes['message'] = '成功'
                        a = datetime.now()
                        User.query.filter(User.mobile==mobile).update({'login_time':a})
                    else:
                        mes['code'] = 138148
                        mes['message'] = "密码错误"
        return jsonify(mes)  
#退出登录
@user_blue.route("/logout")
def logout():
    # print(session.get('username'))
    session.pop('username')
    return redirect("/")

#显示用户中心
@user_blue.route("/user_info")
@isLogin
def user_info():
    user = g.user
    data = {'user_info':user}
    return render_template("news/user.html",data=data)

#修改个人资料
@user_blue.route("/base_info",methods=['post','get'])
@isLogin
def base_info():
    user = g.user
    mes = {}
    if request.method == "POST":
        signature = request.form.get('signature')
        nick_name = request.form.get('nick_name')
        gender = request.form.get('gender')
        joy = request.form.get('joy')
        language = request.form.get('language')
        if not all([signature,nick_name,gender,language]):
            mes['code'] = 10010
            mes['mes'] = "信息不完整"
        else:
            # upermes={'signature':signature,'nick_name':nick_name,'gender':gender,'joy':int(joy),'language':int(language)}
            user = User.query.filter(User.id==user.id).first()
            if user:
                # User.query.filter(User.id==user.id).update(upermes)
                user.nick_name = nick_name
                user.signature = signature
                user.gender=gender
                user.joy = joy
                user.language = int(language)
                db.session.add(user)
                mes['code'] = 200
                mes['message'] = '修改成功'
            else:
                mes['code'] = 10010
                mes['message'] = '修改失败'
        return jsonify(mes)
    jlist = []
    if user.joy:
        jlist = [int(i) for i in user.joy.split(",")]
    joylist = [{'id':1,'name':'唱歌'},{'id':2,'name':'跳舞'},{'id':3,'name':'看书'}]
    data = {'user_info':user,'joylist':joylist,'jlist':jlist}
    return render_template("news/user_base_info.html",data=data)

# 修改密码
@user_blue.route("/pass_info",methods=['post','get'])
@isLogin
def pass_info():
    user = g.user
    data = {'user_info':user}
    user_id = session.get('user_id')
    mes = {}
    if request.method == "POST":
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        new_password2 = request.form.get('new_password2')
        if not all([old_password,new_password,new_password2]):
            mes['code'] = 10010
            mes['message'] = "信息不完整"
        else:
            pwd = check_password_hash(user.password_hash,old_password)
            if pwd:
                if new_password == new_password2:
                    haha = User.query.filter_by(id=user_id).update({'password_hash':generate_password_hash(new_password2)})
                    mes['code'] = 200
                    mes['message'] = '修改成功'
                else:
                    mes['code'] = 10012
                    mes['message'] = '两次密码不一致'
            else:
                mes['code'] = 10018
                mes['message'] = '当前密码错误'
        return jsonify(mes)

    return render_template("news/user_pass_info.html",data=data)

#头像设置
@user_blue.route("/pic_info",methods=['get','post'])
@isLogin
def pic_info():
    user = g.user
    if request.method == "POST":
        image = request.files['avatar']
        file_name = photos.save(image)
        #更新数据库
        user.avatar_url = "/static/upload/"+file_name
        db.session.add(user)
    data = {'user_info':user}
    return render_template("news/user_pic_info.html",data=data)

#新闻发布
@user_blue.route("/news_release",methods=['get','post'])
@isLogin
def news_release():
    userid = g.user.id
    if request.method == "POST":
        data = request.form
        title = data.get('title','')
        category_id = data.get('category_id','')
        digest = data.get('digest','')
        image = request.files['index_image']
        image_url = ''
        if image:
            image_name = photos.save(image)
            image_url = "static/upload/"+image_name
        content = data.get('content','')
        new = News(user_id=userid,name=title,descrp=digest,image_url=image_url,content=content,is_exam=0,reason='',cid=category_id)
        db.session.add(new)
        return redirect(url_for('user.news_list'))
    #获取分类信息
    news = News_type.query.all()
    data = {'news':news}
    return render_template("news/user_news_release.html",data=data)

#新闻列表
@user_blue.route("/news_list")
@isLogin
def news_list():
    user = g.user
    current_page = 1
    try:
        p = int(request.args.get('p',0))
    except:
        p=0
    if p > 0:
        current_page = p
    page_count = admin_news_count
    news_list = News.query.filter(News.user_id==user.id).paginate(current_page,page_count,False)
    data = {'news_list':news_list.items,'current_page':news_list.page,'total_page':news_list.pages,'user_info':user}
    return render_template("news/user_news_list.html",data=data)

#图片上传
@user_blue.route("/upload_img",methods=['post','get'])
def upload_img():
    image = request.files['file']
    file_name = photos.save(image)
    mes = {}
    mes['path'] = "/static/upload/"+file_name
    mes['error'] = False
    return jsonify(mes)



#我的关注
@user_blue.route("/user_follow")
@isLogin
def user_follow():
    user = g.user
    current_page = request.args.get('p',1)
    page_count=1
    author_list = user.user_followed.paginate(int(current_page),page_count,False)

    data = {'author_list':author_list.items,'current_page':author_list.page,'total_page':author_list.pages}
    return render_template("news/user_follow.html",data=data)



# 我的收藏
@user_blue.route("/collection")
@isLogin
def collection():
    user = g.user
    current_page = request.args.get('p',1)
    page_count=1
    news_list = user.user_collect.paginate(int(current_page),page_count,False)

    data = {'user_info':user,'news_list':news_list.items,'current_page':news_list.page,'total_page':news_list.pages}
    return render_template("news/user_collection.html",data=data)



