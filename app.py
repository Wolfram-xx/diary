import os

import bcrypt
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from model import *
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
login_m = LoginManager(app)
login_m.login_view = 'hello'
db = DB()

@login_m.user_loader
def load_user(user_id):
    user = db.get_user_by_id(user_id)
    if user:
        return User(user[0], user[1])
    return None

@app.route('/')
def hello():
    return render_template("index.html")

@app.route('/profile/')
@login_required
def profile():
    notes = db.get_notes_by_owner(current_user.id)
    return render_template("profile.html", user=current_user, notes=notes)
@app.route('/auth/', methods=['POST'])
def auth():
    if request.method == 'POST':
        login = request.form.get('login')
        passw = request.form.get('pass')
        user_data = db.get_user_by_login(login)
        if user_data:
            id, login, hash_pass = user_data
            if bcrypt.checkpw(passw.encode(), hash_pass.encode()):
                user = User(id, login)
                login_user(user)
                return redirect(url_for('profile'))
        return "Wrong login or password", 401

    return render_template("index.html")

@login_required
@app.route("/profile/newnote/")
def newnote():
    return render_template("newnote.html")

@login_required
@app.route("/create_note/", methods=['POST'])
def create_new_note():
    if request.method == "POST":
        descript = request.form.get('description')
        title = request.form.get('title')
        if title:
            db.add_note(descript, current_user.id, title)
            return redirect("/profile")
    return redirect("/newnote")

@login_required
@app.route("/note/")
def show_note():
    note_id = request.args.get('id')
    if note_id:
        note = db.get_note_by_id(note_id)
        if note:
            if note[3] == current_user.id:
                return render_template("note.html", note=note)

@login_required
@app.route("/editnote/", methods=['POST'])
def editnote():
    note_id = request.form.get("id")
    note = db.get_note_by_id(note_id)
    if note:

        if note[3] == current_user.id:
            title = request.form.get("title")
            description = request.form.get("description")
            db.edit_note(note_id, title, description)
            return redirect("/profile")

@login_required
@app.route("/delnote/", methods=['POST'])
def delnote():
    note_id = request.form.get("id")
    note = db.get_note_by_id(note_id)
    if note:
        if note[3] == current_user.id:
            db.delnote(note_id)
            return redirect('/profile')
@login_required
@app.route('/changestatus', methods=['POST'])
def changestatus():
    note_id = request.form.get('id')
    note = db.get_note_by_id(note_id)
    if note:
        if note[3] == current_user.id:
            if note[5] == "inwork":
                db.setnotestatus(note_id, "ready")
            if note[5] == "ready":
                db.setnotestatus(note_id, "inwork")
            return redirect(f'/note/?id={note_id}')

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')
@app.route('/reg/', methods=['POST'])
def reg():
    login = request.form.get('login')
    passw = request.form.get('pass')
    user_id = db.add_user(login, bcrypt.hashpw(passw.encode(), bcrypt.gensalt()).decode())
    user = User(user_id, login)
    login_user(user)
    return redirect('/profile/')


if __name__ == '__main__':
    app.run(debug=True)