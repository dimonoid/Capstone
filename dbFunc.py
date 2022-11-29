from flask import Flask, render_template, Response, flash
import os
from flask import request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3

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

#class to declare a license plate    
class Plate(db.Model):
    id=db.Column(db.String(7), primary_key=True, nullable = False, unique=True)
    name=db.Column(db.String(100), nullable=False)
    info=db.Column(db.String(500), nullable=False)
    
    def __repr__(self):
        return f'<Plate {self.id}>'        

#class to declare a criminal
class Face(db.Model):
    name=db.Column(db.String(18), primary_key=True, nullable= False, unique=True)
    info=db.Column(db.String(500), nullable=False)
    
    def __repr__(self):
        return f'<Face {self.name}>'

#compare string detected from license plate to plate table in database
def plate_detected(str):
    conn = sqlite3.connect('Database.db')
    cur=conn.cursor()
    cur.execute("SELECT * FROM LicensePlate WHERE one=?", (columnchosen,))
     
    records = cur.fetchall()
    for row in records:
        if(row[0] == str):
            print("License Plate Number: ", row[0])
            print("Owner: ", row[1])
            print("Infractions: ", row[2])
            print("/n")     
    cur.close()

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

#compare string of person's name to database
def compare_face(str):
	conn = sqlite3.connect('Database.db')
	cur=conn.cursor()
	cur.execute("SELECT * FROM Criminals WHERE one=?", (columnchosen,))
	
	records = curr.fetchall()
	for row in records:
		if(row[0] == str):
			print("Name: ", row[0])
			print("Crimes: ", row[1])
			print("/n")
		
	cur.close()