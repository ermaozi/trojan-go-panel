from flask import render_template
from flask.views import MethodView

__all__ = ["Index"]


class Index(MethodView):
    def get(self):
        return render_template("index.html")
