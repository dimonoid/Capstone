from flask import Flask, render_template, Response, flash
import os
from flask import request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from collections import deque

from sqlalchemy.sql import func

db = SQLAlchemy()

def init_dbFunc():
    dbFunc = Flask(__name__, instance_relative_config=False)
    dbFunc.config.from_object('config.Config')
    
    db.init_dbFunc(dbFunc)
    
    with app.app_context():
        from . import routes #import routes
        db.create_all()
        
        return dbFunc


#compare string detected from license plate to plate table in database
def plate_detected(str):
    conn = sqlite3.connect('Database.db')
    cur=conn.cursor()
    cur.execute("SELECT * FROM LicensePlate WHERE one=?", (columnchosen,))
     
    records = cur.fetchall()
    for row in records:
        if(row[0] == str):
            d = deque(row[0], row[1], row[2])
    cur.close()
    return d
    
#compare string of person's name to database
def compare_face(str):
    conn = sqlite3.connect('Database.db')
    cur=conn.cursor()
    cur.execute("SELECT * FROM Criminals WHERE one=?", (columnchosen,))
	
    records = curr.fetchall()
    for row in records:
        if(row[0] == str):
            d = deque(row[0], row[1])
    cur.close()
    return d

#add License Plate to database
def add_plate(LicensePlate, Owner, Info):
	try:
		con = sql.connect('Database.db')
		c = con.cursor()
		c.execute("INSERT INTO LicensePlate (LicensePlate, Owner, Info) VALUES (%s, %s, %s)" %(LicensePlate, Owner, Info))
		con.commit()
	except:
		print("Error adding plate to db")

#add Face to database
def add_face(Name, Crime):
	try:
		con=sql.connect('Database.db')
		c=con.cursor()
		c.execute("INSERT INTO Criminals (Name, Crime) VALUES (%b, %s, %s)" %(Name, Crime))
		con.commit()
	except:
		print("Error adding face to db")
