from flask.app import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from main.models.mode import *
from main.models.exts import db

# 初始化应用
app = Flask(__name__)

# 从config中加载配置文件内容 config上线模式 devConfig开发模式
app.config.from_object("conf.flask.config.DevelopmentConfig")

db.init_app(app)

# 初始化migrate
migrate = Migrate(app, db)

# 初始化manager
manager = Manager(app)

# command加载DB命令,可以使用migrate
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()