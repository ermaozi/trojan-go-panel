from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler


db = SQLAlchemy()
bcrypt = Bcrypt()
scheduler = APScheduler()
