import psycopg2
try: 
  connection = psycopg2.connect(user = "si18_master",
                                password = "9v29KW9xr6gNuXPys64aJLwVJEsJHXUg",
                                host = "209.240.107.6",
                                port = "5432",
                                database = "si18data_production")
  cursor = connection.cursor()
  cursor.execute('SELECT id, operator_id FROM operations ORDER BY id ASC LIMIT 5')
  x = cursor.fetchall()
  print(f"Query in PostgreSQL: {x}")
  cursor.execute("SELECT version();")
  record = cursor.fetchone()
  print("You are connected to - ", record,"\n")

except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while conecting PostgreSQL table", error)

finally:
  if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")

'''
create_table_query = ''/'CREATE TABLE mobile
          (ID INT PRIMARY KEY     NOT NULL,
          MODEL           TEXT    NOT NULL,
          PRICE         REAL); ''/'
'''