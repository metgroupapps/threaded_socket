import sys
import json 
import yaml 
import logging
import time
import redis
import psycopg2
from psycopg2 import sql
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
r = redis.Redis(host='209.240.107.6', port="6379", password="XBLB!RVfj3a[H/%WcykDa;Wk5@xTZf<") 
formatter = logging.Formatter("%(asctime)s:%(levelname)s - %(message)s")
handler = TimedRotatingFileHandler('info_log.log', when="midnight", interval=1, encoding='utf8')
handler.suffix = "%d-%m-%Y"
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
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
            if ("PARAMETER" in loaded_json):
              operation = loaded_json['OPERATION']
              if operation == "CONNECT":
                self.session_id = loaded_json['SESSION']
                self.deviceId = loaded_json['PARAMETER']['DSNO']
                self.autocar = loaded_json['PARAMETER']['AUTOCAR'] 
                self.gpsdate, self.currenttime, self.curtime, self.etime, self.stime, self.starttime, self.endtime = 0, 0, 0, 0, 0, 0, 0
                self.connectionReply(operation)
              elif operation == "KEEPALIVE":
                reply = json.dumps({"MODULE":"CERTIFICATE","OPERATION":"KEEPALIVE","SESSION":self.session_id})  
                self.connectionMessage(reply)
              elif operation == "SPI":
                self.handleSPIMessages(loaded_json, connection)
              else:
                if operation == "SENDALARMINFO":
                  replyAlarm = {"MODULE":"CERTIFICATE","OPERATION":operation,"RESPONSE":{"ERRORCAUSE":"SUCCESS","ERRORCODE":0,"ALARMTYPE":loaded_json['PARAMETER']['ALARMTYPE'],"CMDTYPE":loaded_json['PARAMETER']['CMDTYPE'],"ALARMUID":loaded_json['PARAMETER']['ALARMUID'],"RUN":loaded_json['PARAMETER']['RUN'],"CMDNO":loaded_json['PARAMETER']['CMDNO']},"SESSION":self.session_id}
                  self.connectionMessage(replyAlarm)
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
    if data['OPERATION'] == 'SPI' and data['PARAMETER']['M'] == 1 and data['PARAMETER']['REAL'] == 0:
      date = parse(data['PARAMETER']['P']['T'] + "-05:00")
      self.gpsdate = date.strftime('%Y/%m/%d %H:%M:%S %z')
      msg_speed = data['PARAMETER']['P']['S']/100
      pValues = {'gpsStatus': data['PARAMETER']['P']['V'], 'latitude': data['PARAMETER']['P']['W'], 'longitude': data['PARAMETER']['P']['J'], 'speed': msg_speed, 'angle': data['PARAMETER']['P']['C']}
      data['PARAMETER']['P'] = pValues
      self.createOnDb(connection, data)
    else: 
      self.handleAlarms(data, connection)

  def handleAlarms(self, data, connection):
    dataInside = data['PARAMETER']
    if ("P" in dataInside):
      date = parse(dataInside['P']['T'] + "-05:00")
      self.gpsdate = date.strftime('%Y/%m/%d %H:%M:%S %z')
      finalValues = {'gpsStatus': dataInside['P']['V'], 'latitude': dataInside['P']['W'], 'longitude': dataInside['P']['J'], 'speed': dataInside['P']['S'], 'angle': dataInside['P']['C']}
      dataInside['P'] = finalValues
      data['PARAMETER'] = dataInside
    if ("CURRENTTIME" in dataInside):
      alertTime = utc.localize(datetime.utcfromtimestamp(dataInside["CURRENTTIME"]))
      self.currenttime = alertTime.astimezone(colombia).strftime('%Y/%m/%d %H:%M:%S %z')
    if ("CURTIME" in dataInside):
      alertTime = utc.localize(datetime.utcfromtimestamp(dataInside["CURTIME"]))
      self.curtime = alertTime.astimezone(colombia).strftime('%Y/%m/%d %H:%M:%S %z')
    if ("ETIME" in dataInside):
      etime = parse(dataInside['ETIME'] + "-05:00")
      self.etime = etime.strftime('%Y/%m/%d %H:%M:%S %z')
    if ("STIME" in dataInside):
      stime = parse(dataInside['STIME'] + "-05:00")
      self.stime = stime.strftime('%Y/%m/%d %H:%M:%S %z')
    if ("STARTTIME" in dataInside):
      starttime = parse(dataInside['STARTTIME'] + "-05:00")
      self.starttime = starttime.strftime('%Y/%m/%d %H:%M:%S %z')
    if ("ENDTIME" in dataInside):
      endtime = parse(dataInside['ENDTIME'] + "-05:00")
      self.endtime = endtime.strftime('%Y/%m/%d %H:%M:%S %z')
    self.createOnDb(connection, data)
  
  def createOnDb(self, connection, values):
    try:
      cursor = connection.cursor()
      strVal = json.dumps(values)
      timeNow = datetime.now(utc).astimezone(colombia).strftime('%Y/%m/%d %H:%M:%S %z')
      sql_values = {"device_id": self.deviceId, "vehicle_internal_code": self.autocar, "parsed_data": strVal, "created_at": timeNow,"updated_at": timeNow}
      dataInside = values['PARAMETER']
      if ("P" in dataInside): 
        sql_values["gps_date"] = self.gpsdate
      if ("CURRENTTIME" in dataInside):
        sql_values["current_time"] = self.currenttime
      if ("CURTIME" in dataInside):
        sql_values["cur_time"] = self.curtime
      if ("ETIME" in dataInside):
        sql_values["end_time"] = self.etime
      if ("STIME" in dataInside):
        sql_values["s_time"] = self.stime
      if ("STARTTIME" in dataInside):
        sql_values["start_time"] = self.starttime
      if ("ENDTIME" in dataInside):
        sql_values["end_time"] = self.endtime
      sql_query = self.saveOnDb(cursor, sql_values)
      logging.debug("Parsed Msg: {}".format(sql_query))
      cursor.execute(sql_query)
      connection.commit()
      cursor.close()
      r.publish('check_mvrs', self.deviceId)
    except (Exception) as error: #, psycopg2.Error
      if(connection):
        logging.error("createOnDb: {}".format(error))
    
  def saveOnDb(self, cursor, baseInfo):
    table = 'mvr_messages'
    columns = list(baseInfo.keys())
    values  = list(baseInfo.values())
    query_string = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
      sql.Identifier(table),
      sql.SQL(', ').join(map(sql.Identifier, columns)),
      sql.SQL(', ').join(sql.Placeholder()*len(values)),
      ).as_string(cursor)
    final_query = cursor.mogrify(query_string, values)
    return final_query

  def timeoutConnection(self):
    self.transport.abortConnection()


def main():
  print("Running TCP Server On Port 8443...")
  factory = protocol.ServerFactory()  
  factory.protocol = TCPServerMVR
  reactor.listenTCP(8443,factory)
  reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()