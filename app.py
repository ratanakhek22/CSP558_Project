from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)
app.secret_key = 'mysupersecretkey'

# SQLAlchemy config (ORM demo uses a separate db file to keep things isolated)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_orm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- ORM Model ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()
    if not User.query.first():
        db.session.add_all([
            User(username='admin', password='admin'),
            User(username='alice', password='alice123')
        ])
        db.session.commit()

# Landing Page
@app.route('/')
def index():
    return render_template('index.html')

# -----------------
# Vulnerable Routes
# -----------------
@app.route('/vuln/login', methods=['GET', 'POST'])
def vuln_login():
    """
    Vulnerable to login bypass via:
        ' OR '1'='1' --
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = conn.execute(query).fetchone()
        conn.close()

        if user:
            session['username'] = user[1]
            return render_template('profile.html', username=session.get('username'), mode='Vulnerable')
        flash("Invalid username or password")

    return render_template('vuln_login.html')


@app.route('/vuln/union', methods=['GET', 'POST'])
def vuln_union():
    """
    Vulnerable to UNION-based data exfiltration via:
        ' UNION SELECT 1, group_concat(username || ':' || password), 'x' FROM users --
    """
    result = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = conn.execute(query).fetchone()
        conn.close()

        result = user

    return render_template('vuln_union.html', result=result)

# -----------
# Safe Routes
# -----------
@app.route('/safe/login/parameterized', methods=['GET', 'POST'])
def safe_parameterized():
    """
    Uses parameterized queries. The query and data are sent
    separately so injected input is never interpreted as SQL.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        user = conn.execute(query, (username, password)).fetchone()
        conn.close()

        if user:
            session['username'] = user[1]
            return render_template('profile.html', username=session.get('username'), mode='Parameterized Query')
        flash("Invalid username or password")

    return render_template('safe_login.html', mode='Parameterized Query', route='safe_parameterized')


@app.route('/safe/login/orm', methods=['GET', 'POST'])
def safe_orm():
    """
    Uses SQLAlchemy ORM. Input is handled by the ORM layer,
    which never interpolates user input directly into SQL.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = user.username
            return render_template('profile.html', username=session.get('username'), mode='ORM')
        flash("Invalid username or password")

    return render_template('safe_login.html', mode='ORM (SQLAlchemy)', route='safe_orm')


if __name__ == '__main__':
    app.run(debug=True)