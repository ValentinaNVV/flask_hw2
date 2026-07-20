from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "секретный-ключ"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    text = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.String(120))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    token = db.Column(db.String(32), unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

#with app.app_context():
#    db.create_all()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    hashed_password = generate_password_hash(request.form.get("password"))
    new_user = User(
        username=request.form.get("username"),
        email=request.form.get("email"),
        password_hash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    user = User.query.filter_by(username=request.form.get("username")).first()
    if user and check_password_hash(user.password_hash, request.form.get("password")):
        user.token = secrets.token_hex(16)
        user.token_expiration = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        session["token"] = user.token
        session["user_id"] = user.id
        return redirect(url_for("index"))
    flash("Неверный логин или пароль")
    return redirect(url_for("login"))

@app.route("/home")
def home():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    user = User.query.get(user_id)
    if not user or not user.token_expiration or user.token_expiration < datetime.utcnow():
        return redirect(url_for("login"))
    return render_template("home.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/notes")
def notes():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    
    user = User.query.get(user_id)
    if not user or not user.token_expiration or user.token_expiration < datetime.utcnow():
        return redirect(url_for("login"))
    
    all_notes = Notes.query.all()
    return render_template("notes.html", entries=all_notes)

@app.route("/add_note", methods=["POST"])
def add_note():
    title = request.form.get("title")
    subtitle = request.form.get("subtitle")
    text = request.form.get("text")
    new_note = Notes(title=title, subtitle=subtitle, text=text)
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for("notes"))

if __name__ == "__main__":
    app.run(debug=True)