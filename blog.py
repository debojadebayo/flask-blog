#blog.py - controller 

#defines imnports, configurations and each view. 

#imports 

from flask import Flask, render_template, request, session, \
flash, redirect, url_for, g

from functools import wraps
import sqlite3

#configuration 

DATABASE = 'blog.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY= "b'\xf0\x1eI\x82$\x90u\xda[\xbf\xf0\x19\xc0S\x91BS\x18\xf5\xd9k\x95\x1b'"

app= Flask(__name__)
#pulls in app configuration by looking for upper case varioables 

app.config.from_object(__name__)

#function used to connect to database. 

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

#tests whether person is logged in 
def login_required(test):
	@wraps(test)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return test(*args,**kwargs)
		else:
			flash("You need to login first.")
			return redirect(url_for('login'))
	return wrap

#function used to login
@app.route('/', methods=['GET', 'POST'])
def login():
	error= None
	status_code= 200 
	if request.method=='POST':
		if request.form['username']!= app.config['USERNAME'] or \
				request.form['password']!= app.config['PASSWORD']:
			error= "Invalid Credentials. Please try again"
			status_code= 401
		else:
			session['logged_in']= True
			return redirect(url_for('main'))
	return render_template('login.html', error=error), status_code

@app.route('/main')
@login_required
def main():
	g.db= connect_db()
	cur= g.db.execute('select * from posts')
	posts= [dict(title= row [0], post = row [1]) for row in cur.fetchall()]
	g.db.close()
	return render_template('main.html', posts= posts)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash("You were logged out")
	return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
@login_required
def add():
	title= request.form['title']
	post= request.form['post']
	if not title or not post:
		flash("All fields are required. Please try again")
		return redirect(url_for('main'))
	else:
		g.db= connect_db()
		g.db.execute('Insert into posts (title, post) values(?, ?)',[request.form['title'], request.form['posts']])
		g.db.commit()
		g.db.close()
		flash("New entry was successfully posted")
		return redirect(url_for('main'))

if __name__ == '__main__':
	app.run(debug=True)