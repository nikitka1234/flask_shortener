import string
import random

from flask import Flask, render_template, redirect, url_for

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


class URLForm(FlaskForm):
    url = StringField("Вставьте ссылку", validators=[DataRequired(message="Поле не должно быть пустым"),
                                                     URL(message="Неверная ссылка")])
    submit = SubmitField("Получить короткую ссылку")


app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET_KEY"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"

db = SQLAlchemy(app)


class URLModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(40), unique=True, nullable=False)
    visits = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow())


with app.app_context():
    db.create_all()


def get_short():
    while True:
        short = ''.join(random.choices(string.ascii_letters + string.ascii_letters, k=6))
        if URLModel.query.filter(URLModel.short == short).first():
            continue
        return short


@app.route("/", methods=["GET", "POST"])
def index():
    form = URLForm()

    if form.validate_on_submit():
        url_model = URLModel()

        url_model.url = form.url.data
        url_model.short = get_short()

        db.session.add(url_model)
        db.session.commit()

        return redirect(url_for("urls"))

    return render_template("index.html", form=form)


@app.route("/urls")
def urls():
    urls_list = URLModel.query.all()

    return render_template("urls.html", urls_list=urls_list)


@app.route("/<string:shorts>")
def url_redirect(shorts):
    url = URLModel.query.filter(URLModel.short == shorts).first()

    if url:
        url.visits += 1

        db.session.add(url)
        db.session.commit()

        return redirect(url.url)

    return shorts
