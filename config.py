#config.py
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

