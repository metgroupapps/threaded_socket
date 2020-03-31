import sys
import socket
import argparse
import threading
import logging
import yaml 
import psycopg2
import json 
from json import JSONDecoder
import time
import re
from datetime import datetime

logging.basicConfig(filename='developer_info.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

conf = yaml.load(open('application.yml'), Loader=yaml.BaseLoader)
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
	sck.listen()
	#records = get_vehicles()
except Exception as e:
	raise SystemExit("We could not bind the server on host: {} to port: {}, because: {}".format(args.host, args.port, e))

def on_new_client(client, connection):
	ip = connection[0]
	port = connection[1]
	logging.info("The new connection was made from IP: {}, and port: {}!".format(ip, port))
	while True:
		msg = client.recv(1024)
		logging.info("Clean data: {}".format(msg))
		handle_message(client, msg)
	client.close()
	logging.info("The client from ip: {}, and port: {}, has gracefully disconnected!".format(ip, port))

def handle_message(client, message):
	strMsg = message.strip().decode('utf-8', 'ignore')
	if len(strMsg) > 0:
		index = strMsg.find("{")
		tmp = strMsg[index:]
		loaded_json = json.loads(tmp)
		print(loaded_json)
		operation = loaded_json['OPERATION']
		session_id = loaded_json['SESSION']
		if operation == "CONNECT":
			#device_id = loaded_json['PARAMETER']['DSNO']
			reply = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"CONNECT","RESPONSE":{"DEVTYPE":1,"ERRORCAUSE":"","ERRORCODE":0,"MASKCMD":1,"PRO":"1.0.4","VCODE":""},"SESSION":session_id})
			client.send(reply.encode('utf-8'))
			#time.sleep(0.5)
			#set_binary = json.dumps({"MODULE":"CONFIGMODEL","OPERATION":"SET","PARAMETER":{"MDVR":{"KEYS":{"GV":1},"PGDSM":{"PGPS":{"EN":1}},"PIS":{"PC041245T":{"GU":{"EN":1,"IT":5}}},"PSI":{"CG":{"UEM":0}}}},"SESSION":session_id})
			#client.send(set_binary.encode('utf-8'))
		elif operation == "KEEPALIVE":
			reply = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"KEEPALIVE","SESSION":session_id})
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
