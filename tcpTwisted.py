import json 
import yaml 
import psycopg2
import logging
from logging.handlers import TimedRotatingFileHandler
from struct import pack, unpack
from datetime import datetime
from twisted.internet import reactor, protocol
from twisted.protocols.policies import TimeoutMixin

FIRST_PART = pack('i', 0)
END_PART = pack('<i', 82)
logging.basicConfig(filename='developer_info.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
conf = yaml.load(open('application.yml'), Loader=yaml.BaseLoader)

class TCPServer(protocol.Protocol, TimeoutMixin):

  def connectionMade(self):
    self.setTimeout(40)
    peer = self.transport.getPeer()
    logging.info("MVR: ip-> {}, port-> {}".format(peer.host, peer.port))

  def dataReceived(self, data):
    if len(data) > 1
      logging.debug("Clean data: {}".format(data))
      strMsg = data.strip().decode('utf-8', 'ignore')
      try:
        index = strMsg.find("{")
        tmp = strMsg[index:]
        loaded_json = json.loads(tmp)
        operation = loaded_json['OPERATION']
        session_id = loaded_json['SESSION']
        self.connectionReply(session_id, operation)
        self.resetTimeout()
      except Exception as e:
        logging.error("Failed fam!: {}".format(e))
        print("Failed fam!: {}".format(e))
    
  def connectionReply(self, session_id, operation):
    if operation == "CONNECT":
      payloadJson = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"CONNECT","RESPONSE":{"DEVTYPE":1,"ERRORCAUSE":"","ERRORCODE":0,"MASKCMD":1,"PRO":"1.0.5","VCODE":""},"SESSION":session_id})
      #payloadJsonBinary = json.dumps({"MODULE":"CONFIGMODEL","OPERATION":"SET","PARAMETER":{"MDVR":{"KEYS":{"GV":1},"PGDSM":{"PGPS":{"EN":1}},"PIS":{"PC041245T":{"GU":{"EN":1,"IT":5}}},"PSI":{"CG":{"UEM":0}}}},"SESSION":session_id})
      self.connectionMessage(payloadJson)
      #self.connectionMessage(payloadJsonBinary)
    elif operation == "KEEPALIVE":
      reply = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"KEEPALIVE","SESSION":session_id})  
      self.connectionMessage(reply)

  def connectionMessage(self, payloadJson):
    payload = str(payloadJson).replace(" ", "")
    pLength = len(payload)
    midPart = pack('>i', pLength)
    completeMessage = FIRST_PART + midPart + END_PART + payload.encode('utf-8')
    self.transport.write(completeMessage)

  def timeoutConnection(self):
    self.transport.abortConnection()

'''
def get_vehicles():
	connection = psycopg2.connect(user = conf['db']['user'], password = conf['db']['password'], host = conf['db']['host'], port = conf['db']['port'], database = conf['db']['database'])
	cursor = connection.cursor()
	cursor.execute('SELECT id, internal_code FROM vehicles ORDER BY id ASC')
	x = cursor.fetchall()
	if(connection):
		cursor.close()
		connection.close()
	return x
'''

def main():
  print("Running TCP Server")
  factory = protocol.ServerFactory()  
  factory.protocol = TCPServer
  reactor.listenTCP(8443,factory)
  reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()