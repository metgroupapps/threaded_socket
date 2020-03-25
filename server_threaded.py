import socket
import argparse
import threading
import logging
import yaml 
import psycopg2

conf = yaml.load(open('application.yml'))

parser = argparse.ArgumentParser(description = "This is the server for the multithreaded socket demo!")
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostname())
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 8443)
args = parser.parse_args()

print(f"Running the server on: {args.host} and port: {args.port}")

sck = socket.socket()
sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try: 
	sck.bind((args.host, args.port))
	sck.listen(5)
	connection = psycopg2.connect(user = conf['db']['user'],
                                password = conf['db']['password'],
                                host = conf['db']['host'],
                                port = conf['db']['port'],
                                database = conf['db']['database'])
  cursor = connection.cursor()
	'''cursor.execute('SELECT id, operator_id FROM operations ORDER BY id ASC LIMIT 5')
  x = cursor.fetchall()
  print(f"Query in PostgreSQL: {x}")
  cursor.execute("SELECT version();")
  record = cursor.fetchone()
	if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")'''
except Exception as e:
	raise SystemExit(f"We could not bind the server on host: {args.host} to port: {args.port}, because: {e}")

def on_new_client(client, connection):
	ip = connection[0]
	port = connection[1]	
	while True:
		msg = client.recv(1024)
		handle_message(msg)
	client.close()

def handle_message(messasge):
	if messasge.decode() == 'exit':
		break
	logging.info(f"The new connection was made from IP: {ip}, and port: {port}!")
	logging.debug(messasge.decode())
	logging.info(f"The client from ip: {ip}, and port: {port}, has gracefully disconnected!")
	#reply = "OK"
	#client.sendall(reply.encode('utf-8'))

while True:
	try: 
		client, ip = sck.accept()
		threading._start_new_thread(on_new_client,(client, ip))
	except KeyboardInterrupt:
		print(f"Gracefully shutting down the server!")
	except Exception as e:
		print(f"Well I did not anticipate this: {e}")

sck.close()