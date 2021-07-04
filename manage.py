import os
import sys

from flask.app import Flask
from flask_cors import CORS

# sys.path.append(os.path.realpath(__file__ + "/.."))

from main.models.exts import bcrypt, db
from main.models.modetool import creat_db
from main.urls.main import init_url

# config = 'conf.flask.config.ProductionConfig'
config = 'conf.flask.config.DevelopmentConfig'

app = Flask(__name__, static_folder="./web/static", template_folder="./web")
CORS(app)

app.config.from_object(config)

db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    creat_db()
    init_url(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
