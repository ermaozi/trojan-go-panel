from flask.app import Flask
from flask_cors import CORS

from main.models.exts import bcrypt, db, scheduler
from main.models.modetool import create_db
from main.urls.main import init_url


def create_app(config_path):
    app = Flask(__name__,
                static_folder="./web/static",
                template_folder="./web")
    CORS(app)

    app.config.from_object(config_path)

    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        create_db()
        init_url(app)

    scheduler.init_app(app)
    scheduler.start()

    return app


if __name__ == '__main__':
    app = create_app("conf.flask.config.DevelopmentConfig")
    app.run(host="0.0.0.0", port=8000)
else:
    app = create_app("conf.flask.config.ProductionConfig")
