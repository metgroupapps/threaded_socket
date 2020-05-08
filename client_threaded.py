import socket
import argparse
import time
import json

parser = argparse.ArgumentParser(description="This is the client")
parser.add_argument('--timeout', metavar = 'timeout', type = float, nargs = '?', default = 0.5)
parser.add_argument('--host', metavar='host', type=str, nargs='?', default=socket.gethostname())
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 8443)
args = parser.parse_args()

print(f"Connecting to server: {args.host} on port: {args.port}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sck:
	try:
		sck.connect((args.host, args.port))
	except Exception as e:
		raise SystemExit(f"We have failed to connect to host: {args.host} on port: {args.port}, because: {e}")

	while True:
		msg = b'\x08\x00\x00\x00\x00\x00\x02&R\x00\x00\x00{"MODULE":"CERTIFICATE","OPERATION":"CONNECT","PARAMETER":{"AUTOCAR":"A1099","AUTONO":"0","CARNUM":"FVK 909","CHANNEL":16,"CID":1818717765,"CNAME":"CUSTOMER_04.1519","DEVCLASS":4,"DEVNAME":"MDVR","DEVTYPE":1,"DLIP":[{"LIP":"192.168.1.100","MT":"eth0"}],"DLP":[80,9006],"DSNO":"0098000163","EID":"APSI18_80","EV":"V1.1","FSV":0,"LINENO":"no disponi","MAC":[{"IMAC":"00:00:00:00:00:00","MT":"eth0"}],"MODE":1,"MTYPE":79,"NET":2,"PRO":"1.0.5","STYPE":74,"TSE":1,"UNAME":"no disponi","UNO":"no disponi"},"SESSION":"ccd944ec-289e-422c-ba25-36e9d7f31483"}\n'
		sck.sendall(msg)
		time.sleep(args.timeout)
		msg2 = b'\x08\x00\x00\x00\x00\x00\x01\xbfR\x00\x00\x00{"MODULE":"EVEM","OPERATION":"SENDALARMINFO","PARAMETER":{"ALARMAS":1,"ALARMCOUNT":1,"ALARMTYPE":56,"ALARMUID":11,"CMDNO":158335004,"CMDTYPE":1,"CURRENTTIME":1588897147,"EVTUUID":"16f32ff5-55fc-4f4a-a235-d5b95b736ad1","L":1,"LEV":1,"P":{"C":34880,"J":"-74.109395","S":0,"T":"20200508051906","V":0,"W":"4.708228"},"RUN":2416,"S":null,"SP":0,"ST":1,"STORAGEINDEX":1,"TRIGGERTYPE":1},"SESSION":"ccd944ec-289e-422c-ba25-36e9d7f31483","TYPE":"NOTIFY"}\n\x08\x00\x00\x00\x00\x00\x01\xbfR\x00\x00\x00{"MODULE":"EVEM","OPERATION":"SENDALARMINFO","PARAMETER":{"ALARMAS":1,"ALARMCOUNT":1,"ALARMTYPE":56,"ALARMUID":11,"CMDNO":158335005,"CMDTYPE":0,"CURRENTTIME":1588897161,"EVTUUID":"16f32ff5-55fc-4f4a-a235-d5b95b736ad1","L":1,"LEV":1,"P":{"C":34880,"J":"-74.109395","S":0,"T":"20200508051920","V":0,"W":"4.708228"},"RUN":2416,"S":null,"SP":0,"ST":1,"STORAGEINDEX":1,"TRIGGERTYPE":1},"SESSION":"ccd944ec-289e-422c-ba25-36e9d7f31483","TYPE":"NOTIFY"}\n'
		sck.sendall(msg2)
		time.sleep(args.timeout)
		if msg2 =='exit':
			print("Client is saying goodbye!")
			break
		data = sck.recv(1024)
		print("The server's response was: {}".format(data))
		time.sleep(15)
