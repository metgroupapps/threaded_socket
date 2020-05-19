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
		print(1)
		time.sleep(1)
		msg2 = b'\x08\x00\x00\x00\x00\x00\x01\xbfR\x00\x00\x00{"MODULE":"EVEM","OPERATION":"SENDALARMINFO","PARAMETER":{"ALARMAS":1,"ALARMCOUNT":1,"ALARMTYPE":56,"ALARMUID":11,"CMDNO":158335004,"CMDTYPE":1,"CURRENTTIME":1588897147,"EVTUUID":"16f32ff5-55fc-4f4a-a235-d5b95b736ad1","L":1,"LEV":1,"P":{"C":34880,"J":"-74.109395","S":0,"T":"20200508051906","V":0,"W":"4.708228"},"RUN":2416,"S":null,"SP":0,"ST":1,"STORAGEINDEX":1,"TRIGGERTYPE":1},"SESSION":"ccd944ec-289e-422c-ba25-36e9d7f31483","TYPE":"NOTIFY"}\n\x08\x00\x00\x00\x00\x00\x01\xbfR\x00\x00\x00{"MODULE":"EVEM","OPERATION":"SENDALARMINFO","PARAMETER":{"ALARMAS":1,"ALARMCOUNT":1,"ALARMTYPE":56,"ALARMUID":11,"CMDNO":158335005,"CMDTYPE":0,"CURRENTTIME":1588897161,"EVTUUID":"16f32ff5-55fc-4f4a-a235-d5b95b736ad1","L":1,"LEV":1,"P":{"C":34880,"J":"-74.109395","S":0,"T":"20200508051920","V":0,"W":"4.708228"},"RUN":2416,"S":null,"SP":0,"ST":1,"STORAGEINDEX":1,"TRIGGERTYPE":1},"SESSION":"ccd944ec-289e-422c-ba25-36e9d7f31483","TYPE":"NOTIFY"}\n'
		sck.sendall(msg2)
		print(2)
		time.sleep(1)
		msg3 = b'\x08\x00\x00\x00\x00\x00\x00\x00R\x00\x00\x00'
		sck.sendall(msg3)
		print(3)
		time.sleep(1)
		msg4 = b'\x16\x03\x01\x00\x8c\x01\x00\x00\x88\x03\x03\x17\x9a\xc9\x15+\x1c\xccsp\x9f\x88f\x0f\xbb\xd0\xf1\x93\x91\x0c\xc6\xd8\x11>\x0b4&\xdbG\x14ZOb\x00\x00\x1a\xc0/\xc0+\xc0\x11\xc0\x07\xc0\x13\xc0\t\xc0\x14\xc0\n\x00\x05\x00/\x005\xc0\x12\x00\n\x01\x00\x00E\x00\x00\x00\x13\x00\x11\x00\x00\x0e67.231.254.162\x00\x05\x00\x05\x01\x00\x00\x00\x00\x00\n\x00\x08\x00\x06\x00\x17\x00\x18\x00\x19\x00\x0b\x00\x02\x01\x00\x00\r\x00\n\x00\x08\x04\x01\x04\x03\x02\x01\x02\x03\xff\x01\x00\x01\x00'
		sck.sendall(msg4)
		print(4)
		time.sleep(1)
		msg5 = b'\x08\x00\x00\x00\x00\x00\x02nR\x00\x00\x00{"MODULE":"DEVEMM","OPERATION":"SPI","PARAMETER":{"M":2,"REAL":0,"S":{"ALARM":0,"G3":3,"G3S":3,"G4":0,"G4S":0,"RE":[2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0],"S":0,"SINFO":[{"DS":0,"LS":0,"O":0,"S":0,"T":0,"TS":2000330686464},{"DS":0,"LS":2457862144,"O":0,"S":0,"T":0,"TS":2000330686464}],"STC":2,"SU":0,"SW":0,"T":"20200508010216","TD":4000,"TM":"81288.035000","TRAFFIC":[{"I":"","RX":0,"T":0,"TS":0,"TX":0},{"I":"","RX":0,"T":1,"TS":0,"TX":0},{"I":"","RX":0,"T":2,"TS":0,"TX":0},{"I":"","RX":0,"T":3,"TS":0,"TX":0}],"V":2460,"VS":[0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1],"W":1,"WS":0}},"SESSION":"ccd944ec-289e-422c-ba25-36e9d7f31483"}\n'
		sck.sendall(msg5)
		print(5)
		time.sleep(1)
		msg6 = b'\x08\x00\x00\x00\x00\x00\x00\x90R\x00\x00\x00{"MODULE":"DEVEMM","OPERATION":"SPI","PARAMETER":{"M":1,"P":{"C":0,"J":"-74.109406","S":0,"T":"20200508010216","V":0,"W":"4.708176"},"REAL":0}}\n'
		sck.sendall(msg6)
		print(6)	
		data = sck.recv(1024)
		print("The server's response was: {}".format(data))
		time.sleep(15)
		break
