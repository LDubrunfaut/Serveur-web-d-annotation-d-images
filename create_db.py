#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('data.db')

print "Opened database successfully";

# DROP TABLE
conn.execute('''DROP TABLE IMAGE;''')
conn.execute('''DROP TABLE ANNOTATION;''')
conn.execute('''DROP TABLE EXAMEN;''')

# TABLE CREATION
conn.execute('''CREATE TABLE EXAMEN
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       PATIENT                  TEXT        NOT NULL,
       PATH_PROTOCOLE           TEXT        NOT NULL,
       PATH_ANALYSE             TEXT        NOT NULL);''')

print "Table created successfully";

# TABLE CREATION
conn.execute('''CREATE TABLE IMAGE
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       NAME                         TEXT        NOT NULL,
       PATH_IMAGE                   TEXT        NOT NULL,
       PATH_THUMB                   TEXT        NOT NULL,
       PATH_ANO                     TEXT        NOT NULL,
       CREATION_DATE                DATETIME    NOT NULL,
       MODIFICATION_DATE            DATETIME    NOT NULL,
       KEYWORDS                     TEXT        NOT NULL,
       AUTEUR                       TEXT        NOT NULL,
       ID_EXAMEN                    INT         NOT NULL,
       FOREIGN KEY(ID_EXAMEN) REFERENCES EXAMEN(ID));''')

print "Table created successfully";

# TABLE CREATION
conn.execute('''CREATE TABLE ANNOTATION
       (ID INTEGER PRIMARY KEY AUTOINCREMENT,
       X1                       FLOAT        NOT NULL,
       Y1                       FLOAT        NOT NULL,
       H                        FLOAT        NOT NULL,
       W                        FLOAT        NOT NULL,
       CREATION_DATE            DATETIME     NOT NULL,
       MODIFICATION_DATE        DATETIME     NOT NULL,
       ANNOTATION               TEXT         NOT NULL,
       AUTEUR                   TEXT         NOT NULL,
       NAME_IMG                 TEXT         NOT NULL,
       COLOR_R                  INTEGER      NOT NULL,
       COLOR_G                  INTEGER      NOT NULL,
       COLOR_B                  INTEGER      NOT NULL,
       FOREIGN KEY(NAME_IMG) REFERENCES IMAGE(NAME));''')

print "Table created successfully";

conn.execute("INSERT INTO EXAMEN (PATIENT,PATH_PROTOCOLE,PATH_ANALYSE) \
      VALUES ('BOURASSIN', 'static/protocoles/protocole1.pdf', 'static/analyses/analyse1.pdf')");
conn.commit()
conn.execute("INSERT INTO EXAMEN (PATIENT,PATH_PROTOCOLE,PATH_ANALYSE) \
      VALUES ('NDEBI', 'static/protocoles/protocole2.pdf', 'static/analyses/analyse2.pdf')");
conn.commit()
conn.execute("INSERT INTO EXAMEN (PATIENT,PATH_PROTOCOLE,PATH_ANALYSE) \
      VALUES ('BORGES', 'static/protocoles/protocole3.pdf', 'static/analyses/analyse3.pdf')");
conn.commit()

conn.close()
