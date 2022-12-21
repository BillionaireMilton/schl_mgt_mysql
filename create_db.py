import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password"
)
db_name = 'schl_mgt'
dbs = []
mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for db in mycursor:
  spec_db_names = db[0].split("'")[0]
  # print(spec_db_names)
  dbs.append(spec_db_names)

# print('________________________')
# print(dbs)

if db_name in dbs:
  print('database already exist')
else:
  mycursor.execute("CREATE DATABASE {}".format(db_name))
  mycursor.execute("SHOW DATABASES")
  dbs.clear
  for db in mycursor:
    spec_db_names = db[0].split("'")[0]
    print(spec_db_names)
    dbs.append(spec_db_names)

  if db_name in dbs:
    print('database created successfully')
