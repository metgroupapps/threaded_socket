import sys
import json 
import yaml 
import logging
import time
import psycopg2
from logging.handlers import TimedRotatingFileHandler
from struct import pack, unpack
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from bitstring import BitArray
from twisted.internet import reactor, protocol
from twisted.protocols.policies import TimeoutMixin

FIRST_PART = pack('i', 0)
END_PART = pack('<i', 82)
logging.basicConfig(filename='developer_info.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
conf = yaml.load(open('application.yml'), Loader=yaml.BaseLoader)
utc = timezone('UTC')
colombia = timezone('America/Bogota')

class TCPServerMVR(protocol.Protocol, TimeoutMixin):

  def connectionMade(self):
    self.setTimeout(40)
    peer = self.transport.getPeer()
    self.ipAddr = peer.host
    self.port = peer.port
    logging.info("MVR: ip-> {}, port-> {}".format(peer.host, peer.port))

  def dataReceived(self, data):
    logging.debug("Clean data: {}".format(data))
    try:
      connection = psycopg2.connect(user = conf['db']['user'], password = conf['db']['password'], host = conf['db']['host'], port = conf['db']['port'], database = conf['db']['database'])
      if  data[0:3] != b'\x16\x03\x01' or data[0:3] != b'\x03\x00\x00':
        if data[0:2] == b'\x08\x00' and data[7:8] != b'\x00':
          newData = data.split(b'\n')
          finalData = [var for var in newData if var]
          for line in finalData:
            strMsg = line.strip().decode('utf-8', 'ignore')
            index = strMsg.find("{")
            tmp = strMsg[index:]
            loaded_json = json.loads(tmp)
            operation = loaded_json['OPERATION']
            if operation == "CONNECT":
              self.session_id = loaded_json['SESSION']
              self.deviceId = loaded_json['PARAMETER']['DSNO']
              self.autocar = loaded_json['PARAMETER']['AUTOCAR']
              self.connectionReply(operation)
            elif operation == "KEEPALIVE":
              reply = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"KEEPALIVE","SESSION":self.session_id})  
              self.connectionMessage(reply)
            elif operation == "SPI":
              self.handleSPIMessages(loaded_json, connection)
            elif operation == "SENDALARMINFO":
              self.handleAlarms(loaded_json, connection)
        elif data[0:2] == b'\x08\x16':
          payloadJsonBinary = json.dumps({"MODULE":"CONFIGMODEL","OPERATION":"SET","PARAMETER":{"MDVR":{"KEYS":{"GV":0},"PGDSM":{"PGPS":{"EN":1}},"PIS":{"PC041245T":{"GU":{"EN":1,"IT":5}}},"PSI":{"CG":{"UEM":0}}}},"SESSION":self.session_id})
          self.connectionMessage(payloadJsonBinary)
    except Exception as e: 
      logging.error("Failed fam!: {}".format(e))
    finally:
      if (connection):
        connection.close()
    self.resetTimeout()
    
  def connectionReply(self, operation):
    if operation == "CONNECT":
      payloadJson = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"CONNECT","RESPONSE":{"DEVTYPE":1,"ERRORCAUSE":"","ERRORCODE":0,"MASKCMD":1,"PRO":"1.0.5","VCODE":""},"SESSION":self.session_id})
      payloadJsonBinary = json.dumps({"MODULE":"CONFIGMODEL","OPERATION":"SET","PARAMETER":{"MDVR":{"KEYS":{"GV":0},"PGDSM":{"PGPS":{"EN":1}},"PIS":{"PC041245T":{"GU":{"EN":1,"IT":5}}},"PSI":{"CG":{"UEM":0}}}},"SESSION":self.session_id})
      self.connectionMessage(payloadJson)
      self.connectionMessage(payloadJsonBinary)

  def connectionMessage(self, payloadJson):
    payload = str(payloadJson).replace(" ", "")
    pLength = len(payload)
    midPart = pack('>i', pLength)
    completeMessage = FIRST_PART + midPart + END_PART + payload.encode('utf-8')
    self.transport.write(completeMessage)
  
  def handleSPIMessages(self, data, connection):
    if data['PARAMETER']['M'] == 1 and data['PARAMETER']['REAL'] == 0:
      date = parse(data['PARAMETER']['P']['T'] + "-05:00")
      finalValues = {'gpsStatus': data['PARAMETER']['P']['V'], 'latitude': data['PARAMETER']['P']['W'], 'longitude': data['PARAMETER']['P']['J'], 'speed': data['PARAMETER']['P']['S'], 'angle': data['PARAMETER']['P']['C'], 'date': date.strftime('%y/%m/%d %H:%M:%S %z')}
      self.createOnDb(connection, finalValues, 0)

  def handleAlarms(self, data, connection):
    dataInside = data['PARAMETER']
    print(dataInside)
    if ("P" in dataInside):
      print("p")
      date = parse(dataInside['P']['T'] + "-05:00")
      finalValues = {'gpsStatus': dataInside['P']['V'], 'latitude': dataInside['P']['W'], 'longitude': dataInside['P']['J'], 'speed': dataInside['P']['S'], 'angle': dataInside['P']['C'], 'date': date.strftime('%y/%m/%d %H:%M:%S %z')}
      dataInside['P'] = finalValues
    if ("CURRENTTIME" in dataInside):
      print('current')
      alertTime = utc.localize(datetime.utcfromtimestamp(dataInside["CURRENTTIME"]))
      dataInside["CURRENTTIME"] = alertTime.astimezone(colombia).strftime('%y/%m/%d %H:%M:%S %z')
    if ("CURTIME" in dataInside):
      print("cur")
      alertTime = utc.localize(datetime.utcfromtimestamp(dataInside["CURTIME"]))
      dataInside["CURTIME"] = alertTime.astimezone(colombia).strftime('%y/%m/%d %H:%M:%S %z')
    if ("ETIME" in dataInside):
      print("et") 
      etime = parse(dataInside['ETIME'] + "-05:00")
      dataInside['ETIME'] = etime.strftime('%y/%m/%d %H:%M:%S %z')
    if ("STIME" in dataInside):
      print("st")
      stime = parse(dataInside['STIME'] + "-05:00")
      dataInside['STIME'] = stime.strftime('%y/%m/%d %H:%M:%S %z')
    if ("STARTTIME" in dataInside):
      print("stt")
      starttime = parse(dataInside['STARTTIME'] + "-05:00")
      dataInside['STARTTIME'] = starttime.strftime('%y/%m/%d %H:%M:%S %z')
    if ("ENDSTIME" in dataInside):
      print("ent")
      endtime = parse(dataInside['ENDTIME'] + "-05:00")
      dataInside['ENDTIME'] = endtime.strftime('%y/%m/%d %H:%M:%S %z')
    data['PARAMETER'] = dataInside
    self.createOnDb(connection, data, 1)
  
  def createOnDb(self, connection, values, typeMsg):
    try:
      cursor = connection.cursor()
      sql = "INSERT INTO mvr_messages(device_id, vehicle_internal_code, kind, parsed_data, created_at, updated_at) VALUES(%s,%s,%s,%s,%s,%s)"
      strVal = json.dumps(values)
      timeNow = datetime.utcnow()
      storeValues= (self.deviceId, self.autocar, typeMsg, strVal, timeNow, timeNow)
      cursor.execute(sql, storeValues)
      connection.commit()
      cursor.close()
      logging.debug("Parsed Msg: {}".format(storeValues))
    except (Exception) as error: #, psycopg2.Error
      if(connection):
        logging.error("Failed to parse: {}".format(error))

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
