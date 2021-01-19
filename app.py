#app.py
from flask import Flask, render_template,make_response, request, redirect, url_for, flash, session, g, jsonify
from flask_mysqldb import MySQL, MySQLdb
from functools import wraps
import bcrypt
import pymysql
import os
import sys
import mysql.connector
import pymysql.cursors
 

app = Flask(__name__)
app.secret_key = os.urandom(24) 
mysql = MySQL(app)  
app.config["app"]=app
app.config["mysql"]=mysql

# MySQL configurations
app.config['MYSQL_USER'] = 'b039c14e7ece2e'
app.config['MYSQL_PASSWORD'] = 'ae243740'
app.config['MYSQL_DB'] = 'heroku_148a102e5bd8be9'
app.config['MYSQL_HOST'] = 'eu-cdbr-west-03.cleardb.net'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')   


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE username=%s', (username,))
        user = cur.fetchone()
        if user is None:
            #flash("Error, password or user not match")
            return render_template('login.html')
        elif len(user)>0:
            if bcrypt.hashpw(password,user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                session['firstName'] = user['firstName']
                session['user_id'] = user['user_id']
                session['lastName'] = user['lastName']
                session['username'] = user['username']
                session['department'] = user['department']
                session['email'] = user['email']
                return render_template(('protected.html'))
            else:
                #flash("Error, password or user not match")
                return render_template('login.html')
        else:
                #flash("Error, password or user not match")
                return render_template('login.html')
        cur.close()
    else:
        return render_template('login.html')



@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        username = request.form['username']
        department = request.form['department']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (firstName,lastName,email,department,username,password) VALUES (%s,%s,%s,%s,%s,%s)', (firstName, lastName,email,department,username,hash_password,))
        mysql.connection.commit()
        session['firstName'] = firstName
        session['lastName'] = lastName
        session['username'] = username
        session['department'] = department
        session['email'] = email
        #flash("User is created")
        return redirect("/login")



@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html')   



@app.route('/try1')
def try1():
    if session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM event')
        data = cur.fetchall()
        cur.close()
        return render_template('try1.html', event = data)
    else:
        return redirect('/home')

@app.route('/try2')
def try2():
    if session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM clubs')
        data = cur.fetchall()
        cur.execute('SELECT user_id,firstName,lastName FROM users') 
        president = cur.fetchall() 
        cur.execute('SELECT * FROM users')
        users = cur.fetchall() 
        cur.close()
        return render_template('try2.html', event = data, president = president, users = users)
    else:
        return redirect('/home')    

@app.route('/try3')
def try3():
    if session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
        user = cur.fetchone()   
        sql = "SELECT \
        event_likes.user_id AS user_id, \
        event_likes.event_id AS event_id, \
        event.event_name AS event_name \
        FROM event_likes \
        INNER JOIN event ON event_likes.event_id = event.id \
        WHERE user_id=%s"
        cur.execute(sql,(session['user_id'],))
        last = cur.fetchall()
        sql1 = "SELECT \
        club_likes.user_id AS user_id, \
        club_likes.club_id AS club_id, \
        clubs.clubName AS clubName \
        FROM club_likes \
        INNER JOIN clubs ON club_likes.club_id = clubs.club_id \
        WHERE user_id=%s"
        cur.execute(sql1,(session['user_id'],))
        club = cur.fetchall()
        cur.execute('SELECT * FROM users WHERE department=%s AND username!=%s', (session['department'],session['username'],))
        dp = cur.fetchall()   
        cur.execute('SELECT * FROM clubs WHERE clubPresident=%s', (session['user_id'],))
        cp = cur.fetchall()  
        return render_template('try3.html', user = user, last = last, club=club, dp = dp, cp=cp)
    else:
        return redirect('/home')
 



@app.route('/add_contact', methods=['POST'])
def add_event():
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            event_name = request.form['event_name']
            event_place = request.form['event_place']
            about_event = request.form['about_event']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            cur.execute("INSERT INTO event (event_name, event_place, about_event,start_date,end_date) VALUES (%s,%s,%s,%s,%s)", (event_name, event_place, about_event,start_date,end_date))
            conn.commit()
            #flash('Event Added successfully')
            return redirect('/try1')
    else:
        return redirect('/home')

@app.route('/add_club', methods=['POST'])
def add_club():
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            clubName = request.form['clubName']
            clubPresident = request.form['clubPresident']
            club_place = request.form['club_place']
            club_description = request.form['club_description']
            cur.execute("INSERT INTO clubs (clubName,clubPresident,club_place,club_description) VALUES (%s,%s,%s,%s)", (clubName,clubPresident,club_place,club_description))
            conn.commit()
            #flash('Club Added successfully')
            return redirect('/try2')
    else:
        return redirect('/home')



@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_event(id):
    if session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM event WHERE id = %s', (id))
        data = cur.fetchall()
        cur.close()
        print(data[0])
        return render_template('edit.html', event = data[0])
    else:
        return redirect('/home')

@app.route('/edit2/<id>', methods = ['POST', 'GET'])
def get_club(id):
    if session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM clubs WHERE club_id = %s', (id))
        data = cur.fetchall()
        cur.execute('SELECT user_id,firstName,lastName FROM users') 
        president = cur.fetchall() 
        cur.close()
        return render_template('edit2.html', event = data[0], president = president)
    else:  
        return redirect('/home')

@app.route('/edit3/<id>', methods = ['POST', 'GET'])
def get_user(id):
    if session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
        user = cur.fetchone()
        cur.close()
        return render_template('edit3.html', event = user)  
    else:
        return redirect('/home')
 
@app.route('/update/<id>', methods=['POST'])
def update_event(id):
    if session:
        if request.method == 'POST':
            event_name = request.form['event_name']
            event_place = request.form['event_place']
            about_event = request.form['about_event']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            conn = mysql.connection
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("""
                UPDATE event
                SET event_name = %s,
                    event_place = %s,
                    about_event = %s,
                    start_date = %s,
                    end_date = %s
                WHERE id = %s
            """, (event_name, event_place, about_event, start_date,end_date, id))
            #flash('Event Updated Successfully')
            conn.commit()
            return redirect('/try1')
    else:
        return redirect('/home')


@app.route('/update2/<id>', methods=['POST'])
def update_club(id):
    if session:
        if request.method == 'POST':
            clubName = request.form['clubName']
            clubPresident = request.form['clubPresident']
            club_place = request.form['club_place']
            club_description = request.form['club_description']
            conn = mysql.connection
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("""
                UPDATE clubs
                SET clubName = %s,
                    clubPresident = %s,
                    club_place = %s,
                    club_description = %s
                WHERE club_id = %s
            """, (clubName, clubPresident, club_place,club_description, id))
            #flash('Club Updated Successfully')
            conn.commit()
            return redirect('/try2')
    else:
        return redirect('/home')
 
@app.route('/update3/<id>', methods=['POST'])
def update_user(id):
    if session:
        if request.method == 'POST':
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            email = request.form['email']
            department = request.form['department']
            username = request.form['username']
            conn = mysql.connection
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("""
                UPDATE users
                SET firstName = %s,
                    lastName = %s,
                    email = %s,
                    department = %s,
                    username = %s
                WHERE user_id = %s
            """, (firstName, lastName, email, department,username, id))
            #flash('Event Updated Successfully')
            conn.commit()
            return redirect('/try3')
    else:
        return redirect('/home')



@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_event(id):
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('DELETE FROM event WHERE id = {0}'.format(id))
        conn.commit()
        #flash('Event Removed Successfully')
        return redirect('/try1')
    else:
        return redirect('/home')

@app.route('/delete2/<string:id>', methods = ['POST','GET'])
def delete_club(id):
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('DELETE FROM clubs WHERE club_id = {0}'.format(id))
        conn.commit()
        #flash('Club Removed Successfully')
        return redirect('/try2')
    else:
        return redirect('/home')

@app.route('/delete3/<string:id>', methods = ['POST','GET'])
def delete_user(id):
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('DELETE FROM users WHERE user_id = {0}'.format(id))
        conn.commit()
        #flash('User Removed Successfully')
        dropsession()
        return redirect('/home')
    else:
        return redirect('/home')  

@app.route('/like/<string:id>', methods = ['POST','GET'])
def like(id):
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM event_likes WHERE event_id=%s AND user_id=%s', (id,session['user_id'],))
        temp = cur.fetchone()
        if temp:
            #flash('You already liked this event')
            return redirect('/try1')  
        else:
            cur.execute("INSERT INTO event_likes (event_id, user_id) VALUES (%s,%s)", (id, session['user_id']))
            conn.commit()
            cur.execute('SELECT * FROM event WHERE id=%s', (id,))
            temp = cur.fetchone()
            #flash('You liked the {0} event'.format(temp['event_name']))
            cur.execute("""
                UPDATE event
                SET event_name = %s,
                    event_place = %s,
                    about_event = %s,
                    start_date = %s,
                    end_date = %s,
                    likeNumber = %s
                WHERE id = %s
            """, (temp['event_name'], temp['event_place'], temp['about_event'], temp['start_date'],temp['end_date'],temp['likeNumber']+1, id))
            conn.commit()
            return redirect('/try1')
    else:
        return redirect('/home')

@app.route('/unlike/<string:id>', methods = ['POST','GET'])
def unlike(id):
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM event_likes WHERE event_id=%s AND user_id=%s', (id,session['user_id'],))
        temp = cur.fetchone()
        if temp:
            cur.execute('SELECT * FROM event WHERE id=%s', (id,))
            temp = cur.fetchone()
            #flash('You unliked the {0} event'.format(temp['event_name']))
            cur.execute('SELECT * FROM event_likes WHERE event_id=%s AND user_id=%s', (id,session['user_id'],))
            temp = cur.fetchone()
            cur.execute('DELETE FROM event_likes WHERE id = {0}'.format(temp['id']))
            conn.commit()
            
            cur.execute('SELECT * FROM event WHERE id=%s', (id,))
            temp = cur.fetchone()
            cur.execute("""
                UPDATE event
                SET event_name = %s,
                    event_place = %s,
                    about_event = %s,
                    start_date = %s,
                    end_date = %s,
                    likeNumber = %s
                WHERE id = %s
            """, (temp['event_name'], temp['event_place'], temp['about_event'], temp['start_date'],temp['end_date'],temp['likeNumber']-1, id))
            conn.commit()
            return redirect('/try1')  
        else:
            #flash('You can not unlike an event that you did not like before')
            return redirect('/try1')
    else:
        return redirect('/home')



@app.route('/like2/<string:id>', methods = ['POST','GET'])
def like2(id):
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM club_likes WHERE club_id=%s AND user_id=%s', (id,session['user_id'],))
        temp = cur.fetchone()
        if temp:
            #flash('You already liked this club')
            return redirect('/try2')
        else:
            cur.execute("INSERT INTO club_likes (club_id, user_id) VALUES (%s,%s)", (id, session['user_id']))
            conn.commit()
            cur.execute('SELECT * FROM clubs WHERE club_id=%s', (id,))
            temp = cur.fetchone()
            #flash('You liked the {0} club'.format(temp['clubName']))
            cur.execute("""
                UPDATE clubs
                SET clubName = %s,
                    clubLikes = %s,
                    clubPresident = %s,
                    club_place = %s,
                    club_description = %s
                WHERE club_id = %s
            """, (temp['clubName'], temp['clubLikes']+1, temp['clubPresident'], temp['club_place'],temp['club_description'], id))
            conn.commit()
            return redirect('/try2')
    else:
        return redirect('/home')  

@app.route('/unlike2/<string:id>', methods = ['POST','GET'])
def unlike2(id):
    if session:
        conn = mysql.connection
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM club_likes WHERE club_id=%s AND user_id=%s', (id,session['user_id'],))
        temp = cur.fetchone()
        if temp:
            cur.execute('SELECT * FROM clubs WHERE club_id=%s', (id,))
            temp = cur.fetchone()
            #flash('You unliked the {0} club'.format(temp['clubName']))
            cur.execute('SELECT * FROM club_likes WHERE club_id=%s AND user_id=%s', (id,session['user_id'],))
            temp = cur.fetchone()
            cur.execute('DELETE FROM club_likes WHERE id = {0}'.format(temp['id']))
            conn.commit()
            
            cur.execute('SELECT * FROM clubs WHERE club_id=%s', (id,))
            temp = cur.fetchone()
            cur.execute("""
               UPDATE clubs
                SET clubName = %s,
                    clubLikes = %s,
                    clubPresident = %s,
                    club_place = %s,
                    club_description = %s
                WHERE club_id = %s
            """, (temp['clubName'], temp['clubLikes']-1, temp['clubPresident'], temp['club_place'],temp['club_description'], id))
            conn.commit()
            return redirect('/try2')
        else:
            #flash('You can not unlike an event that you did not like before')
            return redirect('/try2')
    else:
        return redirect('/home')




@app.route('/userPage/<string:id>', methods = ['POST','GET'])
def userPage(id):
    if session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE user_id = {0}'.format(id))
        user = cur.fetchone()
        sql = "SELECT \
        event_likes.user_id AS user_id, \
        event_likes.event_id AS event_id, \
        event.event_name AS event_name \
        FROM event_likes \
        INNER JOIN event ON event_likes.event_id = event.id \
        WHERE user_id=%s"
        cur.execute(sql,(id,))
        last = cur.fetchall()
        return render_template('user.html', user = user, last = last) 
    else:
        return redirect('/home')  



@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    session.clear()
    return render_template('home.html')


@app.route('/protected')
def protected():
    if session:
        return render_template('protected.html')
    else:
        return redirect('/home')


# starting the app
if __name__ == "__main__":
    app.secret_key = "012#GoshsadsSfjd(*)*&"
    app.run()
