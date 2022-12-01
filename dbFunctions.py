### This file will contain all of the functions related to the Database functions ###

import sqlite3

con = sqlite3.Connection('Database.db')
con.row_factory = sqlite3.Row


def find_person(inputName):
    """
    This function will return a dictionary with the name and information of the person
    if they are present in the database.  Returns None if person not found.
    """
    # Check the Criminals table
    cur = con.cursor()
    cur.execute('SELECT * FROM Criminals')

    # Search each row and check to see if name exists
    for row in cur.fetchall():
        if (row[0] == inputName):
            #print("Name of person found: " + row[0])
            #print("Crime: " + row[1])
            return dict(row)

    print("Person was not found in the database!")
    return None


def find_lp_owner(inputPlate, cur):
    """
    This function will return a dictionary with the name of the license plate owner and their crimes
    if they are present in the database.  Returns None if plate is not found.
    """
    # Check the LicensePlates table
    # cur = con.cursor()
    cur.execute('SELECT * FROM LicensePlates')

    # Search each row and check to see if name exists
    for row in cur.fetchall():
        if (row[0] == inputPlate):
            #print("License plate number found: " + row[0])
            #print("Owner: " + row[1])
            #print("Crime: " + row[2])
            return dict(row)

    print("License plate '" + inputPlate + "' was not found in the database!")
    return None


## These are some tests to show that the functions are working
#test1 = find_person("Ahmad")
#print(" ")
#test2 = find_person("Humza")
#print(" ")
#test3 = find_person("Ansh")  # Not in database
#print(" ")
#test4 = find_lp_owner("CTKM993")
#print(" ")
#test5 = find_lp_owner("420blazeit")  # Not in database
#print(" ")
#test6 = find_lp_owner("PL8REC")
