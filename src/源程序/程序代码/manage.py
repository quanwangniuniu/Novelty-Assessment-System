'''
1.导入 Flask-Migrate 和 Flask-Script 扩展，以及应用程序主模块、数据库对象和数据库模型类。
2.创建了 Flask-Script 的 Manager 对象，并将应用程序实例传递给它。
3.创建了一个 Flask-Migrate 的 Migrate 对象，并将应用程序实例和数据库对象传递给它。
4.将 Flask-Migrate 提供的命令行命令 MigrateCommand 添加到 Flask-Script 的 Manager 对象中。
5.判断是否在主模块中执行该脚本，如果是，则执行 Flask-Script 的 Manager 对象的 run() 方法，启动应用程序。
'''


from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from main import app
from extensions import db
from models import User,Item,Comment,Interest

manager = Manager(app)

migrate = Migrate(app,db)

manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()