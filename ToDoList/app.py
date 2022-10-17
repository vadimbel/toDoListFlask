
from flask import Flask, render_template, g, request, redirect, url_for, session
from database import get_db, get_db_notes
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.teardown_appcontext
def close_db_notes(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_current_user():
    user_res = None

    # if user logged in -> session should have 'user' field
    if 'username' in session:
        # then get the username out of the session
        user = session['username']

        db = get_db()
        # get all data of provided username
        user_cur = db.execute(f"SELECT * FROM users WHERE username='{user}'")
        user_res = user_cur.fetchone()

    return user_res


@app.route('/', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    db = get_db()

    # if user is logged in , he should not be able to go to this page
    if user:
        return redirect(url_for('create_note'))

    if request.method == 'POST':
        username = request.form["uname"]
        password = request.form["psw"]

        # create query and check if there is a username with provided password ib db
        data = db.execute(f"SELECT * FROM users WHERE username='{username}'").fetchone()

        # provided username is in db
        if data:
            # check if provided password for this username is valid
            if data[2] == password:
                session['username'] = username
                # password valid -> let user login
                return redirect(url_for('create_note'))

            # password is invalid -> display error message
            return render_template('login.html', password_error='Invalid Password', user=user)

        # provided username is not in db
        return render_template('login.html', username_error='Invalid Username', user=user)

    return render_template('login.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()

    # if user is logged in , he should not be able to go to this page
    if user:
        return redirect(url_for('create_note'))

    # get username & password from - form , then check if provided username already exists in db
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['psw']

        db = get_db()

        data = db.execute(f"SELECT * FROM users WHERE username='{username}'").fetchone()

        # username already exists in db
        if data:
            return render_template('register.html', user=user, username_error='Username is already exists')

        # username not exists -> create new user , then move to main page
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", [username, password])
        db.commit()
        session['username'] = username

        return redirect(url_for('create_note'))

    return render_template('register.html', user=user)


@app.route('/create_note', methods=['GET', 'POST'])
def create_note():
    user = get_current_user()

    # if user in not logged in , he should not be able to go this page
    if not user:
        return redirect(url_for('/'))

    db = get_db_notes()

    # get data provided to form on 'main_page'
    if request.method == 'POST':
        title = request.form['title']
        note = request.form['note']

        # title cannot be empty , if not empty -> insert new note to 'notes' table
        if title:
            db.execute("INSERT INTO notes (username, title, note) VALUES (?, ?, ?)", [session['username'], title, note])
            db.commit()
            return render_template('create_note.html', user=user, message='New note was added')

        return render_template('create_note.html', user=user, error='Title field is empty')

    return render_template('create_note.html', user=user)


@app.route('/my_notes', methods=['GET', 'POST'])
def my_notes():
    user = get_current_user()
    db = get_db_notes()

    # if user in not logged in , he should not be able to go this page
    if not user:
        return redirect(url_for('/'))

    data = db.execute(f"SELECT * FROM notes WHERE username='{session['username']}'").fetchall()

    return render_template('my_notes.html', user=user, notes=data)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

