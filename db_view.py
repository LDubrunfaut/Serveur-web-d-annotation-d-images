#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('data.db')

print "Opened database successfully";

# UPDATE OPERATION
#conn.execute("UPDATE IMAGE set SALARY = 25000.00 where ID=3")
#conn.commit
#print "Total number of rows updated :", conn.total_changes

# DELETE OPERATION
#conn.execute("DELETE from IMAGE where ID=2;")
#conn.commit
#print "Total number of rows deleted :", conn.total_changes

# SELECT OPERATION
cursor = conn.execute("SELECT ID, PATIENT, PATH_PROTOCOLE, PATH_ANALYSE from EXAMEN")
print "In Table EXAMEN";
for row in cursor:
   print "ID = ", row[0]
   print "PATIENT = ", row[1]
   print "PATH_PROTOCOLE = ", row[2]
   print "PATH_ANALYSE = ", row[3],"\n"

cursor = conn.execute("SELECT ID, PATH_IMAGE, PATH_THUMB, PATH_ANO,CREATION_DATE,MODIFICATION_DATE, KEYWORDS, AUTEUR, ID_EXAMEN from IMAGE")
print "In Table IMAGE";
for row in cursor:
   print "ID = ", row[0]
   print "PATH_IMAGE = ", row[1]
   print "PATH_THUMB = ", row[2]
   print "PATH_ANO = ", row[3]
   print "CREATION_DATE = ", row[4]
   print "MODIFICATION_DATE = ", row[5]
   print "KEYWORDS = ", row[6]
   print "AUTEUR = ", row[7]
   print "ID_EXAMEN = ", row[8], "\n"

cursor = conn.execute("SELECT ID,X1,Y1,H,W,CREATION_DATE,MODIFICATION_DATE,ANNOTATION,NAME_IMG, AUTEUR, COLOR_R, COLOR_G, COLOR_B from ANNOTATION")
print "In Table ANNOTATION";
for row in cursor:
   print "ID = ", row[0]
   print "X1 = ", row[1]
   print "Y1 = ", row[2]
   print "H = ", row[3]
   print "W = ", row[4]
   print "CREATION_DATE = ", row[5]
   print "MODIFICATION_DATE = ", row[6]
   print "ANNOTATION = ", row[7]
   print "NAME_IMG = ", row[8]
   print "AUTEUR = ", row[9]
   print "COLOR = ", row[10]
   print "COLOR = ", row[11]
   print "COLOR = ", row[12], "\n"

conn.close()
