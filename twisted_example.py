import sys
import argparse
import threading
import logging
import json 
import yaml 
import psycopg2
from struct import *
from datetime import datetime
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol

FIRST_PART = pack('i', 0)
END_PART = pack('<i', 82)
logging.basicConfig(filename='developer_info.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
conf = yaml.load(open('application.yml'), Loader=yaml.BaseLoader)

class TCPServer(protocol.Protocol):
    
  def dataReceived(self, data):
    strMsg = data.strip().decode('utf-8', 'ignore')
    try:
      index = strMsg.find("{")
      tmp = strMsg[index:]
      loaded_json = json.loads(tmp)
      operation = loaded_json['OPERATION']
      session_id = loaded_json['SESSION']
      if operation == "CONNECT":
        #device_id = loaded_json['PARAMETER']['DSNO']
        self.connectionReply(session_id, operation)
      elif operation == "KEEPALIVE":
        reply = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"KEEPALIVE","SESSION":session_id})    
    except Exception as e:
      logging.error("Failed fam!: {}".format(e))
      print("Failed fam!: {}".format(e))
    
  def connectionReply(self, session_id, operation):
    payloadJson = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"CONNECT","RESPONSE":{"DEVTYPE":1,"ERRORCAUSE":"","ERRORCODE":0,"MASKCMD":1,"PRO":"1.0.4","VCODE":""},"SESSION":session_id})
    payload = str(payloadJson).replace(" ", "")
    pLength = sys.getsizeof(payload)
    midPart = pack('>i', pLength)
    completeMessage = FIRST_PART + midPart + END_PART + payload.encode('utf-8')
    self.transport.write(completeMessage)
    #payloadJsonBinary = json.dumps({"MODULE":"CONFIGMODEL","OPERATION":"SET","PARAMETER":{"MDVR":{"KEYS":{"GV":1},"PGDSM":{"PGPS":{"EN":1}},"PIS":{"PC041245T":{"GU":{"EN":1,"IT":5}}},"PSI":{"CG":{"UEM":0}}}},"SESSION":session_id})
    #payloadBinary = str(payloadJsonBinary).replace(" ", "")
    #pLengthBinary = sys.getsizeof(payloadBinary)
    #midPartBinary = pack('>i', pLengthBinary)
    #completeMessageBinary = FIRST_PART +  midPartBinary + END_PART
    #client.send(completeMessageBinary.encode('utf-8'))  


def main():
  factory = protocol.ServerFactory()
  factory.protocol = TCPServer
  reactor.listenTCP(8443,factory)
  reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()