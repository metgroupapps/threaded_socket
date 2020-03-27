import sys
import socket
import argparse
import threading
import logging
import yaml 
import psycopg2
from datetime import datetime

conf = yaml.load(open('application.yml'), Loader=yaml.BaseLoader)
log_name = "log_threaded_server_{}".format(datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
logging.basicConfig(filename=log_name)

parser = argparse.ArgumentParser(description = "This is the server for the multithreaded socket.")
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostname())
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 8443)
args = parser.parse_args()

print("Running the server on: {} and port: {}".format(args.host, args.port))

sck = socket.socket()
sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def get_vehicles():
	connection = psycopg2.connect(user = conf['db']['user'], password = conf['db']['password'], host = conf['db']['host'], port = conf['db']['port'], database = conf['db']['database'])
	cursor = connection.cursor()
	cursor.execute('SELECT id, internal_code FROM vehicles ORDER BY id ASC')
	x = cursor.fetchall()
	if(connection):
		cursor.close()
		connection.close()
	return x

try: 
	sck.bind((args.host, args.port))
	sck.listen(5)
	#records = get_vehicles()
except Exception as e:
	raise SystemExit("We could not bind the server on host: {} to port: {}, because: {}".format(args.host, args.port, e))

def on_new_client(client, connection):	
	ip = connection[0]
	port = connection[1]
	while True:
		msg = client.recv(1024)
		print("The client said: {}".format(msg.decode()))
		handle_message(client, ip, port, msg)
	logging.info("The client from ip: {}, and port: {}, has gracefully disconnected!".format(ip, port))
	client.close()

def handle_message(client, ip, port, messasge):
	logging.info("The new connection was made from IP: {}, and port: {}!".format(ip, port))
	logging.debug(messasge.decode())
	reply = "OK"
	client.send(reply.encode('utf-8'))

while True:
	try: 
		client, ip = sck.accept()
		threading._start_new_thread(on_new_client,(client, ip))
	except KeyboardInterrupt:
		print("Gracefully shutting down the server!")
		sys.exit()
	except Exception as e:
		print("Well I did not anticipate this: {}".format(e))

sck.close()