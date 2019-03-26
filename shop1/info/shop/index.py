from flask import Blueprint,request,render_template,redirect,url_for,session,flash,jsonify,g
from models import *
from apps import photos
import re
from utils.comm import isLogin
from utils.constant import admin_news_count
index_blue = Blueprint('index',__name__)


#初始化(分类表)数据
@index_blue.route("/addcate")
def addCate():
    cate = Cate(name='苹果类')
    cate1 = Cate(name='香蕉类')
    cate2 = Cate(name='橘子类')
    db.session.add_all([cate,cate1,cate2])
    return "ok"

#初始化(good表)数据
@index_blue.route("/addgoods")
def addGoods():
    good = Goods(name='苹果1',price=1.25,descrip='口感嫩滑',content='哈哈哈哈哈',image_url='/static/upload/1.jpg',number=10,cid=1)
    good1 = Goods(name='苹果2',price=4.5,descrip='超级好吃',content='哈哈哈哈哈',image_url='/static/upload/2.jpg',number=11,cid=1)
    good2 = Goods(name='香蕉1',price=2.15,descrip='口感嫩滑',content='哈哈哈哈哈',image_url='/static/upload/3.jpg',number=12,cid=2)
    good3 = Goods(name='香蕉2',price=3.25,descrip='超级好吃',content='哈哈哈哈哈',image_url='/static/upload/4.jpg',number=13,cid=2)
    good4 = Goods(name='橘子1',price=4.25,descrip='口感嫩滑',content='哈哈哈哈哈',image_url='/static/upload/5.jpg',number=14,cid=3)
    good5 = Goods(name='橘子2',price=5.25,descrip='口感嫩滑',content='哈哈哈哈哈',image_url='/static/upload/6.jpg',number=15,cid=3)    
    db.session.add_all([good,good1,good2,good3,good4,good5])
    return "ok"

@index_blue.route("/")
def index():
    cate = Cate.query.all()
    current_page = request.args.get('p',1)
    #搜索 获取搜索值
    keyword = request.args.get('keyword')
    page_count=5
    #分页
    if keyword:
        good = Goods.query.filter(Goods.name.like('%'+keyword+'%')).paginate(int(current_page),page_count,False)
    else:
        keyword = ''
        good = Goods.query.paginate(int(current_page),page_count,False)
    data = {'good':good.items,'current_page':good.page,'total_page':good.pages,'keyword':keyword}
    return render_template('index/index.html',data=data,cate=cate)



@index_blue.route("/goodlist",methods=['post','get'])
def goodlist():
    cid = request.args.get('id')
    current_page = request.args.get('p',1)
    page_count=1
    goods = Goods.query.filter(Goods.cid==cid).paginate(int(current_page),page_count,False)
    data = {'goods':goods.items,'current_page':goods.page,'total_page':goods.pages,'cid':cid}
    return render_template("index/goodlist.html",data=data)


# 详情页
@index_blue.route("/content")
def content():
    user_id = 0
    id = request.args.get('id',0)
    if session.get("uid"):
        user_id = session.get("uid")
    if int(id)>0:
        goods = Goods.query.filter(Goods.id==id)
    comments = Comment.query.filter(Comment.good_id == id).order_by('create_time').all()
    data = {'goods':goods,'user_id':user_id,'comments':comments}
    return render_template("index/content.html",data=data)



# 创建接口buy 方法为提交（提交到数据库购物车表中）
@index_blue.route("/buy",methods = ['post','get'])
def buy():
    mes = {}
    # 获取用户id
    userid = session.get('uid')
    # 如果未获取到则定义mes
    if not userid:
        mes['code'] = 10011
        mes['message'] = "请登录后操作"
        # 将其返回为json数据
        return jsonify(mes)
    else:
        # 获取到的话通过从页面获取的id获取商品id
        goodid = request.form.get('id')
        #先查询购物车是否为空
        cart = Cart.query.filter(Cart.user_id==userid,Cart.good_id==goodid).first()
        #如果不为空则购买数量加一
        if cart:
            cart.number = cart.number+1
        else:
            #根据商品id查询商品信息
            good= Goods.query.filter(Goods.id==goodid).first()
            # 给购物车内的参数赋值并添加进去
            cart = Cart(user_id=userid,good_id=goodid,number=1,price=good.price,name=good.name)
        db.session.add(cart)
        # 将mes返回为json数据
        mes['code'] = 200
        mes['message'] = '购买成功'
        return jsonify(mes)

# =================================================================================3

# 创建cart接口
@index_blue.route("/cart")
def cart():
    # 查询所有购物车信息并将其渲染到 cart.html 页面
    userid = session.get('uid')
    cart = Cart.query.filter(Cart.user_id==userid).all()
    # cart = Cart.query.all()
    sum = 0
    for i in cart:
        sum += i.number*i.price
    return render_template('index/cart1.html',cart=cart,sum = sum)
    
# =================================================================================4

# 创建login接口 方法为提交（将用户名密码提交并进行判断）
@index_blue.route("/login",methods = ['post','get'])
def login():
    if request.method == "POST":
        # 从登陆页面获取用户名和密码
        name = request.form.get('username')
        password = request.form.get('password')
        # 如果不存在
        if not all([name,password]):
            flash('亲，信息不完整')
        else:
            # 通过过滤取出用户信息（数据库中的用户名与密码和html页面获取到的用户名和密码一致）
            user = User.query.filter(User.name==name,User.password==password).first()
            if user:
                # 将用户名和其id存入session
                session['username'] = name
                session['uid'] = user.id
                # 返回到 find_all 接口
                return redirect(url_for('index.index'))
            else:
                flash('用户密码错误或用户不存在，立即注册！！！')
    return render_template('index/login.html')

# =================================================================================5

# 创建zhuce接口，方法为提交（提交到user数据库中）
@index_blue.route("/zhuce",methods = ['post','get'])
def zhuce():
    if request.method == "POST":
        # 从html页面获取用户名和密码
        name = request.form.get('user')
        pwd = request.form.get('pwd')
        # 判断是否为空
        if not all([name,pwd]):
            flash('账号密码输入不能为空')
        else:
            # 判断正则匹配是否成功
            username = re.match('^\d{11}$',name)
            password = re.match('^.{6}$',pwd)
            if username:
                if password:
                    # 成功的话添加入库
                    user = User(name=str(name), password=str(pwd))
                    db.session.add(user)
                    return redirect(url_for('index.login'))
                else:
                     flash('密码格式不正确')
            else:
                 flash('账号格式不正确')

    return render_template('index/zhu_ce.html')

#发表评论
@index_blue.route("/comm",methods=['post'])
def comm():
    mes = {}
    uid = session.get("uid")
    print(uid)
    good_id = request.form.get('good_id')
    print(good_id)
    content = request.form.get('content')
    print(content)
    if not all([good_id,content]):
        mes['code'] = 10010
        mes['message'] = '参数错误'
    else:
        comment = Comment(content=content,user_id=uid,good_id=good_id)
        db.session.add(comment)
        db.session.commit()
        mes['code'] = 200
        mes['message'] = '评论成功'
    return jsonify(mes)


# 购物车批量删除
@index_blue.route('/dele',methods=['post','get'])
def dele():
    mes = {}
    clist = request.form.getlist('clist')
    for i in clist:
        db.session.execute('delete from cart where id in(%s)' % i)
    mes['code'] = 200
    mes['mes'] = '删除成功'
    return jsonify(mes)