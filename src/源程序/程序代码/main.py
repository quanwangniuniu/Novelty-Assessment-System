'''
视图控制
请求处理
'''

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from flask import Flask,render_template,url_for,request,redirect,session
from textdistance import Levenshtein
import simhash
import config
from extensions import db
from models import User,Item,Comment,Interest
from decorators import login_required
from sqlalchemy.sql import  text
import os
from werkzeug.security import generate_password_hash
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

UPLOAD_PATH = r'F:\张越\二手项目课题平台flask项目\python-second-hand-goods-trading\src\源程序\程序代码\static\images'

def allowfiletype(filename):
    type = filename.split('.')[-1]
    if type in ['png','jpg','bmp','gif']:
        return True
    else:
        return False

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)




# 首页,展示所有发布的课题
@app.route('/')
def index():
    items = {
        'items' : Item.query.filter(Item.isclosed==0).order_by(text('-create_time')).all(),
    }
    return render_template('index.html',**items)

# 登录
@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',somethingwrong=False)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username==username).first()

        # 用户已经注册
        if user and user.checkPassWord(password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html',somethingwrong=True)

# 注销(退出登录)
@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 注册
@app.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('register.html',user_exist=False,password_not_checked=False)
    else:
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        rootuser = True if username=='root' else False
        #user=False
        user = User.query.filter(User.username==username).first()
        if user:
            return render_template('register.html',user_exist=True,password_not_checked=False)
        else:
            if password1!=password2:
                return render_template('register.html',user_exist=False,password_not_checked=True)
            else:
                new_user = User(username=username,email=email,password=password1,authority=rootuser)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))

# 课题相似度分析
def calculate_similarity(itemOne, itemTwo):
    return 100

# 使用余弦相似度计算文本相似度
import math
def cosine_sim(text1, text2):
    dict1 = {}
    for i in range(len(text1) - 2):
        dict1[text1[i:i + 3]] = dict1.get(text1[i:i + 3], 0) + 1
    dict2 = {}
    for i in range(len(text2) - 2):
        dict2[text2[i:i + 3]] = dict2.get(text2[i:i + 3], 0) + 1

    # 创建向量表示并计算余弦相似度
    vector1 = np.array([dict1.get(x, 0) for x in dict1.keys()])
    vector2 = np.array([dict2.get(x, 0) for x in dict1.keys()])
    return  0 if math.isnan(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))) else np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


# 使用Jaccard相似度计算文本相似度
def jaccard_sim(text1, text2):
    set1 = set([text1[i:i+4] for i in range(0, len(text1), 4)])
    set2 = set([text2[i:i+4] for i in range(0, len(text2), 4)])
    return len(set1 & set2) / len(set1 | set2)

# 使用TF-IDF计算文本相似度
def tfidf_sim(text1, text2):
    doc1 = [" ".join([text1[i:i + 3] for i in range(0, len(text1), 3)])]
    doc2 = [" ".join([text2[i:i + 3] for i in range(0, len(text2), 3)])]
    # 计算TF-IDF特征向量
    vectorizer = TfidfVectorizer().fit_transform(doc1 + doc2)
    # 计算余弦相似度
    cos_sim = cosine_similarity(vectorizer[0], vectorizer[1])
    return cos_sim


# 使用SimHash计算文本相似度
def simhash_sim(str1, str2):
    sh1 = simhash.Simhash(str1)
    sh2 = simhash.Simhash(str2)
    return sh1.distance(sh2) / 64  # 64位SimHash值

@app.route('/analysis/',methods=['GET','POST'])
@login_required
def analysis():
    if request.method == 'POST':
        itemOne = request.form['itemOne']
        itemTwo = request.form['itemTwo']
        # 计算课题重复度
        similarity = calculate_similarity(itemOne,itemTwo)
        # 余弦相似度为
        coss = cosine_sim(itemOne,itemTwo)
        # Jaccard相似度为
        jacc = jaccard_sim(itemOne,itemTwo)
        # TF - IDF相似度为
        tf = tfidf_sim(itemOne,itemTwo)
        # SimHash相似度为
        sm = simhash_sim(itemOne,itemTwo)
        contents = {
            'itemOne': itemOne ,
            'itemTwo': itemTwo,
            'coss': float(coss),
            'jacc': jacc,
            'tf': float(tf),
            'sm': sm,
            'cos_score': round(25*(1-float(coss)),3),
            'jacc_score': round(25*(1-jacc),3),
            'tf_score': round(25*round(1-float(tf), 5)),
            'sm_score': round(25*(1-sm),3),
            'overall_score':round(25*(1-float(coss))+25*(1-jacc)+25*(1-float(tf))+25*(1-sm),3)
        }
        return render_template('analysis.html',**contents)
    else:
        return render_template('analysis.html')

# 发布课题
@app.route('/release/',methods=['GET','POST'])
@login_required
def release():
    if request.method == 'GET':
        return render_template('realease_item.html')
    else:
        name = request.form.get('item_name')
        description = request.form.get('item_description')
        price = request.form.get('item_price')
        file = request.files.get('file')
        if file:
            img_name = file.filename
            if allowfiletype(img_name):
                imgurl = os.path.join(UPLOAD_PATH,img_name)
                file.save(imgurl)
            else:
                imgurl = None
        else:
            imgurl = None
        print(imgurl)
        item = Item(name=name,description=description,price=price,imgpath=imgurl)
        userid = session.get('user_id')
        item.owner = User.query.filter(User.id==userid).first()
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('index'))

# 课题详情及评论页面
@app.route('/detail/<itemid>/')
@login_required
def detail(itemid):
    user = User.query.filter(User.id==session.get('user_id')).first()
    root_user = True if user.authority else False
    item = Item.query.filter(Item.id==itemid).first()
    if item.imgpath:
        item_img_name = item.imgpath.split('\\')[-1]
    else:
        item_img_name = ''
    imgpath = url_for('static',filename='images/{}'.format(item_img_name))
    inter = Interest.query.filter(Interest.userid==session.get('user_id'),Interest.itemid==itemid).first()
    if inter:
        flag = True
    else:
        flag = False
    contents = {
        'item_id':item.id,
        'item_name':item.name,
        'item_price':item.price,
        'item_description':item.description,
        'item_owner':item.owner.username,
        'item_createtime':item.create_time,
        'item_imgpath':imgpath,
        'comments':item.comments,
        'owner_email':item.owner.email,
        'flag':flag,
        'rootuser':root_user,
    }
    return render_template('item_detail.html',**contents)

# 在特定课题评论区添加评论
@app.route('/add_comment/',methods=['POST'])
@login_required
def add_comment():
    content = request.form.get('content')
    comment = Comment(content=content)
    ownerid = session.get('user_id')
    user = User.query.filter(User.id==ownerid).first()
    comment.owner = user
    itemid = request.form.get('item-id')
    item = Item.query.filter(Item.id==itemid).first()
    comment.item = item
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail',itemid=itemid))

# 搜索
@app.route('/search/')
@login_required
def search():
    q = request.args.get('q')
    if q:
        items = Item.query.filter(Item.name.contains(q)).order_by(text('-create_time')).all()
    else:
        items = Item.query.order_by(text('-create_time')).all()
    return render_template('index.html',items=items)

# 个人中心
@app.route('/usercenter/<target>/')
def usercenter(target):
    print(target)
    userid = session.get('user_id')
    user = User.query.filter(User.id==userid).first()
    items = user.items
    if target == 'items':
        print('target is items')
        return render_template('usercenter.html',type='item',items=items,flag=1)
    elif target=='profile':
        print('target is profile')
        ##找出用户所有感兴趣的课题
        inters = Interest.query.filter(Interest.userid==userid).all()
        items_id = []
        for inter in inters:
            items_id.append(inter.itemid)
        interested_items = []
        for i in items_id:
            item = Item.query.filter(Item.id==i).first()
            interested_items.append(item)
        return render_template('usercenter.html',user_=user,interested_items=interested_items,type='profile',flag=2)
    elif target=='profile_edit':
        return render_template('usercenter.html',type='profile_edit',flag=3)

# 关闭某个课题
@app.route('/closeitem/<itemid>/')
def closeitem(itemid):
    item = Item.query.filter(Item.id==itemid).first()
    item.isclosed = 1       ##关闭该课题的课题
    db.session.commit()
    return redirect(url_for('usercenter',target='items'))

# 开放某个课题
@app.route('/openitem/<itemid>/')
def openitem(itemid):
    item = Item.query.filter(Item.id==itemid).first()
    item.isclosed = 0       ##关闭该课题的课题
    db.session.commit()
    return redirect(url_for('usercenter',target='items'))

# 彻底删除某个课题(用户)
@app.route('/deleteitem/<itemid>')
def deleteitem(itemid):
    item = Item.query.filter(Item.id == itemid).first()
    comments = item.comments
    for comment in comments:
        db.session.delete(comment)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('usercenter',target='items'))

# 修改课题市场
@app.route('/modify/<itemid>/',methods=['POST'])
def modify(itemid):
    item = Item.query.filter(Item.id == itemid).first()
    new_price = request.form.get('newprice')
    item.price = new_price
    db.session.commit()
    return redirect(url_for('usercenter',target='items'))

# 对某个课题感兴趣
@app.route('/interest/<itemid>/')
def interest(itemid):
    userid = session.get('user_id')
    new_interest = Interest(userid=userid,itemid=itemid)
    db.session.add(new_interest)
    db.session.commit()
    return redirect(url_for('detail',itemid=itemid))

# 取消对某个课题的感兴趣
@app.route('/de_interest/<itemid>/')
def de_interest(itemid):
    userid = session.get('user_id')
    inter = Interest.query.filter(Interest.userid==userid,Interest.itemid==itemid).first()
    db.session.delete(inter)
    db.session.commit()
    return redirect(url_for('detail',itemid=itemid))

# 删除某个发布的课题(管理员)
@app.route('/deleteitem_root/<itemid>/')
def deleteitem_root(itemid):
    item = Item.query.filter(Item.id==itemid).first()
    comments = item.comments
    for comment in comments:
        db.session.delete(comment)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

# 删除评论(管理员)
@app.route('/deletecomment/<commentid>/')
def deletecomment(commentid):
    comment = Comment.query.filter(Comment.id==commentid).first()
    itemid = comment.itemid
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('detail',itemid=itemid))


# 修改个人资料
@app.route('/edit_profile/',methods=['POST'])
def edit_profile():
    userid = session.get('user_id')
    user = User.query.filter(User.id==userid).first()
    new_email = request.form.get('new_email')
    new_password1 = request.form.get('new_password1')
    new_password2 = request.form.get('new_password2')
    if new_password1 != new_password2:
        return render_template('usercenter.html',type='profile_edit',flag=3,password_wrong=True)
    user.email = new_email
    user.password = generate_password_hash(new_password1)
    db.session.commit()
    return redirect(url_for('usercenter',target='profile'))



# 上下文处理函数
@app.context_processor
def mycontextprocessor():
    userid = session.get('user_id')
    # 用户已经登录
    if userid:
        user = User.query.filter(User.id==userid).first()
        return {'user':user.username,'root_user':user.authority}
    else:
        return {'root_user':False}

if __name__ == '__main__':
    app.run()
