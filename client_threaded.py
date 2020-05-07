import socket
import argparse
import time

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
		msg = b'\x08\x00\x00\x00\x00\x00\x01\xf4R\x00\x00\x00{"MODULE":"CERTIFICATE","OPERATION":"CONNECT","PARAMETER":{"AUTOCAR":"prueba","AUTONO":"0","CARNUM":"","CHANNEL":16,"CID":12,"CNAME":"CUSTOMER_04.1519","DEVCLASS":4,"DEVNAME":"MDVR","DEVTYPE":1,"DLIP":[{"LIP":"0.0.0.0","MT":"eth0"}],"DLP":[80,9006],"DSNO":"00980001E4","EID":"APSI18_80","EV":"V1.1","FSV":0,"LINENO":"","MAC":[{"IMAC":"00:00:00:00:00:00","MT":"eth0"}],"MODE":1,"MTYPE":79,"NET":2,"PRO":"1.0.5","STYPE":74,"TSE":1,"UNAME":"","UNO":""},"SESSION":"396c2350-2610-4204-bbbf-a9f65f204f65"}\n'
		sck.sendall(msg)
		time.sleep(args.timeout)
		#x = b'\x08\x00\x00\x00\x00\x00\x00\x90R\x00\x00\x00{"MODULE":"DEVEMM","OPERATION":"SPI","PARAMETER":{"M":1,"P":{"C":0,"J":"-75.730863","S":0,"T":"20200505125858","V":0,"W":"4.796765"},"REAL":0}}\n'
		x = b'\x08\x00\x00\x00\x00\x00\x01\xedR\x00\x00\x00{"MODULE":"EVEM","OPERATION":"SENDALARMINFO","PARAMETER":{"ALARMAS":1,"ALARMCOUNT":1,"ALARMNAME":"Video Loss","ALARMTYPE":0,"ALARMUID":1,"CHANNEL":8191,"CHANNELMASK":1,"CMDNO":13369347,"CMDTYPE":1,"CURRENTTIME":1588323537,"EVTUUID":"dcf55be6-a99f-40ad-954d-4a6cc24a1e63","L":1,"LCH":[0],"P":{"C":0,"J":"-75.730803","S":0,"T":"20200501135859","V":0,"W":"4.796716"},"RUN":204,"SER":"VL","SNO":0,"STORAGEINDEX":0,"TRIGGERTYPE":1},"SESSION":"396c2350-2610-4204-bbbf-a9f65f204f65","TYPE":"NOTIFY"}\n'
		sck.sendall(x)
		time.sleep(args.timeout)

		if msg =='exit':
			print("Client is saying goodbye!")
			break
		data = sck.recv(1024)
		print("The server's response was: {}".format(data))
		time.sleep(15)
