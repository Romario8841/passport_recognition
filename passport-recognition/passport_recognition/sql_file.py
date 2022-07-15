import mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database = "passport"
)
print(mydb)
mycursor = mydb.cursor()
mycursor.execute('CREATE TABLE people(name VARCHAR(500), surname VARCHAR(500), patronymic VARCHAR(500))')
