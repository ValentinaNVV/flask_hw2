from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

diary = {}  # словарь для хранения записей: {заголовок: текст}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/notes")
def notes():
    return render_template("notes.html", entries=diary)

@app.route("/add_note", methods=["POST"])
def add_note():
    title = request.form.get("title")
    text = request.form.get("text")
    diary[title] = text
    return redirect(url_for("notes"))

if __name__ == "__main__":
    app.run(debug=True)