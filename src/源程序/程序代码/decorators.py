'''
设置登录拦截器
'''

from functools import wraps
from flask import session,redirect,url_for

# 登录限制装饰器
def login_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if session.get('user_id'):
            return f(*args,**kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper