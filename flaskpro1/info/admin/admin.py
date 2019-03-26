from flask import Blueprint,render_template,redirect,url_for,session,request,flash,jsonify
import re
from models import *
#生成密码
from werkzeug.security import generate_password_hash,check_password_hash 
from utils.constant import admin_news_count
#初始化
admin_blue = Blueprint('admin',__name__)

#显示登录页面
@admin_blue.route("/login",methods=['post','get'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if not all([username,password]):
            flash('用户名密码不能为空')
        else:
            #用户名必须是数字，字母，下划线和5到8位
            flag = re.match("\w{5,8}$",username)
            if flag == False:
                flash('用户名不合法')
            else:
                admin = Admin.query.filter(Admin.name==username).first()
                if not admin:
                    flash("用户不存在")
                else:
                    flag = check_password_hash(admin.password_hash,password)
                    if flag:
                        session['username'] = username
                        return redirect(url_for('admin.index'))
                    else:
                        flash('密码错误')
    return render_template("admin/login.html")

#初始化管理员
@admin_blue.route('/addadmin')
def add_admin():
    password = generate_password_hash('123')
    admin = Admin(name='admin',password_hash=password)
    db.session.add(admin)
    return "ok"
 
@admin_blue.route('/index')
def index():
    username = session.get('username')
    if not username:
        return redirect(url_for('admin.login'))
    else:
        return render_template('admin/index.html',username=username)

#点击新闻分类管理渲染新闻分类管理news_type.html页面接口
@admin_blue.route('/newscate',methods=['post','get'])
def newscate():
    mes = {}
    if request.method == "POST":
        name1 = request.form.get('name')
        name2 = re.findall('\s+',name1)
        id = request.form.get('id')
        if id:
            news_type = News_type.query.filter(News_type.id==id).first()
            if not news_type:
                mes['code'] = 10018
                mes['message'] = '没有此次信息'
            else:
                news_type.name = name1
                db.session.add(news_type)
                mes['code'] = 200
                mes['message'] = '修改成功'
                return jsonify(mes)
                
        else:
            if name2:
                mes['code'] = 10012
                mes['message'] = '不能有空格'
                return jsonify(mes)     
            else:
                category = News_type.query.filter(News_type.name==name1).first()
                if category:
                    mes['code']=10010
                    mes['message'] = '分类名称已存在'
                    return jsonify(mes)
                else:
                    news_type = News_type(name=name1)
                    db.session.add(news_type)
                    mes['code'] = 200
                    mes['message '] = '添加成功'
                    return jsonify(mes)
    catelist = News_type.query.all()
    return render_template('/admin/news_type.html',catelist=catelist)

@admin_blue.route("/deletecate",methods=['post','get'])
def deletecate():
    if request.method =="POST":
        mes = {}
        id = request.form.get('id')
        news_type = News_type.query.filter(News_type.id==id).delete()
        mes['code'] = 200
        mes['message'] = '删除成功'
        return jsonify(mes)

#用户列表
@admin_blue.route("/user_list")
def user_list():
    current_page = 1
    try:
        p = int(request.args.get('p',0))
    except:
        p=0
    if p > 0:
        current_page = p
    page_count = admin_news_count
    user_list = User.query.order_by(User.update_time.desc()).paginate(current_page,page_count,False)
    data = {'user_list':user_list.items,'current_page':user_list.page,'total_page':user_list.pages}
    return render_template('/admin/user_list.html',data=data)

#新闻审核
@admin_blue.route("/newsreview")
def newsreview():
    current_page = 1
    try:
        p = int(request.args.get('p',0))
    except:
        p=0
    #搜索 获取搜索值
    keyword = request.args.get('keyword')
    if p > 0:
        current_page = p
    page_count = admin_news_count
    #分页
    if keyword:
        news_list = News.query.filter(News.name.like('%'+keyword+'%')).paginate(current_page,page_count,False)
    else:
        keyword = ''
        news_list = News.query.paginate(current_page,page_count,False)
    data = {'news_list':news_list.items,'current_page':news_list.page,'total_page':news_list.pages,'keyword':keyword}
    return render_template('admin/news_review.html',data=data)

#审核
@admin_blue.route("/news_review_detail",methods=['post','get'])
def news_review_detail():
    if request.method == "POST":
        mes = {}
        #获取要更新的值
        id = request.form.get('id')
        action = request.form.get('action')
        reason = request.form.get('reason')
        news = News.query.filter(News.id==id).first()
        if news:
            #存在时更新字段（是否通过）
            news.is_exam = int(action)
            #失败的时候更新原因
            if int(action) == 2:
                news.reason = reason
            db.session.add(news)
            mes['errno'] = 200
            mes['errmsg'] = "审核通过"
        else:
            mes['errno'] = 10010
            mes['errmsg'] = "未找到相应新闻"
        return jsonify(mes)
    id = request.args.get("id")
    news = News.query.filter(News.id==id).first()
    data = {'news':news}
    return render_template("admin/news_review_detail.html",data=data)




#用户统计
# @admin_blue.route("/user_count",methods=['post','get'])
# def user_count():
#     data = {"total":'',"month_total":'',"day_total":''}
#     return render_template('/admin/user_count.html',data=data)


from datetime import datetime,timedelta
#用户统计
@admin_blue.route('/user_count',methods=['get','post'])
def user_count():
    #总共多少用户
    user = User.query.count()
    #每个月有多少用户
    month_date = datetime.strftime(datetime.now(),"%Y-%m-01")
    month_total = User.query.filter(User.login_time>=month_date).count()

    #每天有多少用户
    day_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    day_total = User.query.filter(User.login_time >= day_date).count()

    #一个月的日期
    datelist = []
    daycount = []
    for i in range(31,0,-1):
        starttime = datetime.strptime(day_date, "%Y-%m-%d") - timedelta(days=i)
        endtime = datetime.strptime(day_date, "%Y-%m-%d") - timedelta(days=i-1)
        datelist.append(datetime.strftime(starttime,'%Y-%m-%d'))
        count = User.query.filter(User.login_time >= endtime).count()
        daycount.append(count)
    datelist.reverse()
    daycount.reverse()

    #一个月每天登陆的人数
    data = {'total_count':user,'mon_count':month_total,'day_count':day_total,'datelist':datelist,'daycount':daycount}
    return render_template('admin/user_count.html',data=data)


