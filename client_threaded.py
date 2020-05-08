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
		msg2 = json.dumps({"versionTrama":"1.0.0","idRegistro":"1582846403054","idOperador":"M1","idVehiculo":"M1403","idRuta":"No Disponible","idConductor":"No Disponible","fechaHoraLecturaDato":"2020-02-27T23:33:22","fechaHoraEnvioDato":"2020-02-27T23:33:23","tipoBus":"B","localizacionVehiculo":[{"latitud":"4.707335","longitud":"-74.110078"}],"tipoTrama":"1","tecnologiaMotor":"2","tramaRetransmitida":'false',"tipoFreno":"1","velocidadVehiculo":"0.0","aceleracionVehiculo":"0.01"})
		sck.sendall(msg2.encode())
		time.sleep(args.timeout)
		if msg2 =='exit':
			print("Client is saying goodbye!")
			break
		data = sck.recv(1024)
		print("The server's response was: {}".format(data))
		time.sleep(15)
