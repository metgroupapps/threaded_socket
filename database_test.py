import psycopg2
try: 
  connection = psycopg2.connect(user = "si18_master",
                                password = "9v29KW9xr6gNuXPys64aJLwVJEsJHXUg",
                                host = "209.240.107.6",
                                port = "5432",
                                database = "si18data_production")

  cursor = connection.cursor()

  select_messages_query = 'SELECT id, operator_id FROM operations ORDER BY id ASC LIMIT 5000'
  
  cursor.execute(select_messages_query)
  x = cursor.fetchall()
  print(f"Query in PostgreSQL: {x}")

except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while creating PostgreSQL table", error)

finally:
  if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")