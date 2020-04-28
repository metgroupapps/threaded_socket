import sys
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

class TCPServerMVR(protocol.Protocol, TimeoutMixin):

  def connectionMade(self):
    self.setTimeout(40)
    peer = self.transport.getPeer()
    self.ipAddr = peer.host
    self.port = peer.port
    logging.info("MVR: ip-> {}, port-> {}".format(peer.host, peer.port))

  def dataReceived(self, data):
    if len(data) > 1:
      logging.debug("Clean data: {}".format(data))
      try:
        strMsg = data.strip().decode('utf-8', 'ignore')
        index = strMsg.find("{")
        if index > -1:
          tmp = strMsg[index:]
          loaded_json = json.loads(tmp)
          operation = loaded_json['OPERATION']
          session_id = loaded_json['SESSION']
          self.deviceId = loaded_json['PARAMETER']['DSNO']
          self.connectionReply(session_id, operation)
        else:
          self.handleRegularReports(data)  
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

  def handleRegularReports(self, data):
    size = unpack('>i', data[0:12][4:8])[0] + 12
    splitedData = list(self.chunked(size, data))
    for msg in splitedData:  
      if msg[12:13] == b'\x00':
        gpsStatus = 'ok'
      elif msg[12:13] == b'\x01':
        gpsStatus ='bad'
      else:
        gpsStatus = 'no gps'
      latitude = unpack('>i',msg[20:24])[0]/1000000
      longitude = unpack('>i',msg[16:20])[0]/100000000
      speed =  unpack('>i',msg[24:28])[0]/100
      angle =  unpack('>i',msg[28:32])[0]/100
      altitude =  unpack('>i',msg[32:36])[0]
      date = datetime.strptime(msg[36:].decode('utf-8', 'ignore').rstrip('\x00') + "-05:00", '%Y%m%d%H%M%S%f%z').strftime('%Y/%m/%d %H:%M:%S:%f %z')
      finalValues = {'gpsStatus': gpsStatus, 'latitude': latitude, 'longitude': longitude, 'speed': speed, 'angle': angle, 'altitude': altitude, 'date': date}      
      self.createOnDb(finalValues)

  def chunked(self, size, source):
    for i in range(0, len(source), size):
      yield source[i:i+size]
  
  def createOnDb(self, values):
    #connection = psycopg2.connect(user = conf['db']['user'], password = conf['db']['password'], host = conf['db']['host'], port = conf['db']['port'], database = conf['db']['database'])
    #cursor = connection.cursor()
    sql = """INSERT INTO devices(device_id, vehicle, parsed_data) VALUES(%s,%s,%s);"""
    values= (self.deviceId, '', json.dumps(values))
    print(values)
    #cursor.execute(sql, values)
    #cursor.close()
    #connection.close()

  def timeoutConnection(self):
    self.transport.abortConnection()




def main():
  print("Running TCP Server")
  factory = protocol.ServerFactory()  
  factory.protocol = TCPServerMVR
  reactor.listenTCP(8443,factory)
  reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()