from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    text = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.String(120))

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/notes")
def notes():
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