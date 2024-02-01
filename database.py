import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2121",
    database="login"
)

conn = db.cursor()

conn.execute("""SELECT *""")