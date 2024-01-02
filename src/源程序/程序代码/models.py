'''
 数据库模型构建
'''

from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

# 用户模型
class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(30),nullable=False)
    authority = db.Column(db.Boolean,nullable=False,default=False)

    def __init__(self,*args,**kwargs):
        email = kwargs.get('email')
        username = kwargs.get('username')
        password = kwargs.get('password')
        authority = kwargs.get('authority')

        self.email = email
        self.username = username
        self.authority = authority
        self.password = generate_password_hash(password)

    def checkPassWord(self,input_password):
        return check_password_hash(self.password,input_password)


# 课题模型
class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)      # 课题ID
    name = db.Column(db.String(30),nullable=False)                      # 课题名称
    description = db.Column(db.Text,nullable=True)                      # 课题详细描述
    price = db.Column(db.Float,nullable=False)                          # 课题价格
    imgpath = db.Column(db.String(300),nullable=True)                    # 课题图片url
    ownerid = db.Column(db.Integer,db.ForeignKey('user.id'))            # 课题发布者id
    owner = db.relationship('User',backref=db.backref('items'))         # 课题发布者
    create_time = db.Column(db.DateTime,default=datetime.now)           # 课题发布时间
    isclosed = db.Column(db.Integer,nullable=False,default=0)           # 课题分享是否被关闭，1为关闭

# 评论模型
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)      # 评论ID
    content = db.Column(db.Text,nullable=False)                         # 评论内容
    itemid = db.Column(db.Integer,db.ForeignKey('item.id'))             # 评论课题的ID
    ownerid = db.Column(db.Integer,db.ForeignKey('user.id'))            # 评论发布者ID
    create_time = db.Column(db.DateTime,default=datetime.now)           # 评论发布时间

    item = db.relationship('Item',backref=db.backref('comments',order_by = id.desc()))       # 评论课题
    owner = db.relationship('User',backref=db.backref('comments'))      # 评论发布者


# 用户--课题 感兴趣的模型
class Interest(db.Model):
    __tablename__ = 'interest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer,db.ForeignKey('user.id'))             # 用户ID
    itemid = db.Column(db.Integer,db.ForeignKey('item.id'))             # 课题ID