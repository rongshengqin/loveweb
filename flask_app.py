# -*- coding: utf-8 -*-

from flask import Flask,request,render_template, url_for, redirect,flash
from flask_login import login_user, logout_user, current_user, login_required,LoginManager,UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from io import BytesIO
from PIL import Image, ImageDraw
#from bs4 import BeautifulSoup as sp
import urllib
import requests
import datetime,os
from momentjs import momentjs
proxies = { "http": "http://127.0.0.1:8087"}  
POSTS_PER_PAGE=12
app = Flask(__name__)
#app.config["DEBUG"] = True
app.jinja_env.globals['momentjs'] = momentjs

# database settings
basedir= os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///'+ os.path.join(basedir,'data.sqlite')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#登录相关
app.secret_key='131243432545qqqewr'
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"
# 用户表
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),unique=True)
    password = db.Column(db.String(64))
    posts = db.relationship('Comment', backref='user', lazy='dynamic')
    pictures = db.relationship('Picture', backref='user', lazy='dynamic')

# 帖子表
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# 图片表
class Picture(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    picture_name = db.Column(db.String(4096),unique=True)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# 小说表
class Novel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(4096),unique=True)
    title=db.Column(db.String(4096))
    timestamp = db.Column(db.DateTime)
    
@app.before_request
def before_request():
    pass
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def hello_world():
    # 照片列表
    imgs=Picture.query.all()
    return render_template("index.html",title = 'Home',imgs=imgs,num_img=len(imgs))

@app.route('/msg',methods=["GET", "POST"])
@app.route('/msg/<int:page>',methods=["GET", "POST"])
@login_required
def msgview(page=1):
    if request.method == "GET":
        return render_template("msg.html", title='posts',comments=Comment.query.order_by(Comment.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False))
    if request.method == "POST":
        content=request.form["contents"].strip()
        if content!='':
            co = Comment(content=content,timestamp=datetime.datetime.utcnow(),user=current_user) 
            db.session.add(co)
            db.session.commit()
        return redirect(url_for('msgview'))

# 超级管理员路由
@app.route('/su',methods=["GET", "POST"])
@app.route('/su/<int:page>',methods=["GET", "POST"])
@login_required
def sudo(page=1):
    if current_user.username!='admin':
        return redirect('/')
    if request.method == "GET":
        return render_template("sudo.html", title='admin',us=User.query.order_by(User.id.desc()).paginate(page, POSTS_PER_PAGE, False))
    if request.method == "POST":
        todels = request.form.getlist('todel')
        for i in todels:
            td = User.query.filter_by(id=int(i)).first()
            #logout_user(td)
            db.session.delete(td)
            db.session.commit()
        return redirect(url_for('sudo'))

# 管理帖子的路由
@app.route('/admin',methods=["GET", "POST"])
@app.route('/admin/<int:page>',methods=["GET", "POST"])
@login_required
def admin(page=1):
    if request.method == "GET":
        return render_template("admin.html", title='posts admin',comments=Comment.query.order_by(Comment.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False))
    if request.method == "POST":
        todels = request.form.getlist('todel')
        for i in todels:
            td = Comment.query.filter_by(id=int(i)).first()
            db.session.delete(td)
            db.session.commit()
        return redirect(url_for('admin'))
    
# 管理小说的路由
@app.route('/nv',methods=["GET", "POST"])
@app.route('/nv/<int:page>',methods=["GET", "POST"])
@login_required
def admin_nv(page=1):
    if request.method == "GET":
        return render_template("admin_nv.html", title='posts admin',comments=Novel.query.order_by(Novel.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False))
    if request.method == "POST":
        todels = request.form.getlist('todel')
        for i in todels:
            td = Novel.query.filter_by(id=int(i)).first()
            db.session.delete(td)
            db.session.commit()
        return redirect(url_for('admin_nv'))

# 管理图片的路由
@app.route('/admin_image',methods=["GET", "POST"])
@app.route('/admin_image/<int:page>',methods=["GET", "POST"])
@login_required
def admin_image(page=1):
    if request.method == "GET":
        return render_template("admin_image.html", title='posts admin',ims=Picture.query.order_by(Picture.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False))
    if request.method == "POST":
        todels = request.form.getlist('todel')
        for i in todels:
            td = Picture.query.filter_by(id=int(i)).first()
            db.session.delete(td)
            db.session.commit()
            ph=basedir+"/static/images/"+td.picture_name
            ph2=basedir+"/static/thumb/"+td.picture_name
            os.remove(ph)
            os.remove(ph2)
        return redirect(url_for('admin_image'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #if g.user is not None and g.user.is_authenticated():
            #return redirect('/')
        user=User.query.filter_by(username=request.form["username"]).first()
        if user!=None and user.password==request.form["password"]:
            login_user(user,remember=False)            
            return redirect(request.args.get("next") or '/')
        else:
            if user==None:
                error = 'no this user. Please try again.'
            else:
                error = 'password err. Please try again.'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        #if g.user is not None and g.user.is_authenticated():
            #return redirect('/')
        user=User.query.filter_by(username=request.form["username"]).first()
        if user!=None:
            error = u'用户名已被占用'    
            return render_template('register.html', error=error)
        if request.form["username"].strip()!='' and request.form["password"].strip()!='':
            u=User(username=request.form["username"].strip(),password=request.form["password"].strip())
            db.session.add(u)
            db.session.commit()
            try:
                login_user()
            except:
                pass
            return redirect('/login')
        else:
            error = u'用户名或密码不能为空'
            return render_template('register.html', error=error)
    return render_template('register.html', error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/novel',methods=['GET', 'POST'])
@app.route('/novel/<int:page>',methods=["GET", "POST"])
@login_required
def novel(page=1):
    if request.method == "GET":
        ur=request.args.get('url', '')
        if ur=='':
            return render_template("novel.html", title='posts admin',nvss=Novel.query.order_by(Novel.timestamp.desc()).paginate(page, 20, False))
        else:
            url=urllib.unquote(request.url.split('url=')[1])
            return requests.get(url).text.replace('href="','href="/novel?url=http://www.cool18.com/bbs4/')  
        
    if request.method == "POST":
            url=request.form["contents"].strip()
            if url<>'':
                html = requests.get(url)
                return html.text         
    return render_template("novel.html", title='posts admin',nvss=Novel.query.order_by(Novel.timestamp.desc()).paginate(page, 20, False))

ALLOWED_EXTENSIONS=set(['png','jpg','jpeg','gif','bmp'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload',methods=['GET', 'POST'])
@login_required
def upload():
    if request.method=='GET':
        return render_template('upload.html')
    IMG = request.files['file']
    #print IMG.filename,IMG and allowed_file(IMG.filename)
    if IMG and allowed_file(IMG.filename):
        filename=secure_filename(IMG.filename)
        # 将图片名存入数据库
        try:
            FilePath,Fileext = os.path.splitext(filename)
            Fileext=Fileext.replace('.','')
            if Fileext=='png':
                filename_jpg="{0}.png".format(FilePath)
            else:
                filename_jpg="{0}.jpg".format(FilePath)
                Fileext='JPEG'
            # 保存原图(转成jpg格式)
            img = Image.open(IMG)
            img.save(basedir+"/static/images/"+filename_jpg,Fileext)
            #IMG.save(basedir+"/static/images/"+filename)
            # 保存缩略图
            #img=Image.open(basedir+"/static/images/"+filename)
            base_width = 100
            w_percent = (base_width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            img = img.resize((base_width, h_size),Image.ANTIALIAS)
            img.save(basedir+"/static/thumb/"+filename_jpg,Fileext)
            # 保存到数据库
            p1=Picture(picture_name=filename_jpg,timestamp=datetime.datetime.utcnow(),user=current_user)
            db.session.add(p1)
            db.session.commit()            
            flash(u'上传成功','upload')
            return render_template('upload.html')
        except:
            db.session.remove()  #这一句非常重要
            flash(u'上传失败','upload')
            return render_template('upload.html')
    flash(u'上传失败','upload')
    return render_template('upload.html')


@app.route('/cron',methods=["GET", "POST"])
def cron():
    if request.method == "GET":
        return 'ok'
    if request.method == "POST":
        content=request.json["cron"]
        #print '#######################',content
        if content!='':
            for n in content:
                
                try:
                    co = Novel(url=n[0],title=n[1],timestamp=datetime.datetime.utcnow()) 
                    db.session.add(co)
                    db.session.commit()
                except:
                    db.session.remove()  #这一句非常重要
                    #print n[0]
        return 'ok'

if __name__ == '__main__':
    app.run()