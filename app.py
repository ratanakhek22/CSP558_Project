from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'mysupersecretkey'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """
    Potential Injections:
    ' OR '1'='1' --
    By passes getting the right username and password, will return first row.

    ' UNION SELECT 1, group_concat(username || ':' || password), 'x' FROM users --
    Grabs the users table and combines the data in the right formate to display as one string.
    """

    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    user = conn.execute(query).fetchone()
    conn.close()

    if user:
        session['username'] = user[1]
        return render_template('profile.html', username=session.get('username'))
    flash("Invalid username or password")
    return redirect(url_for('index'))

@app.route('/union')
def union():
    return render_template('UNION.html')

if __name__ == '__main__':
    app.run(debug=True)