import sys
import json 
import yaml 
import logging
import time
import psycopg2
from psycopg2 import sql
from datetime import datetime
from twisted.internet import reactor, protocol
from twisted.protocols.policies import TimeoutMixin
from bitstring import BitArray

logging.basicConfig(filename='developer_info.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
conf = yaml.load(open('application.yml'), Loader=yaml.BaseLoader)
event_kind = {"P20": 0, "P60": 1, "ALA1": 2, "ALA2": 3, "ALA3": 4, "ALA4": 5, "ALA5": 6, "ALA6": 7, "ALA7": 8, "EV1": 9, "EV2": 10, "EV3": 11, "EV4": 12, "EV5": 13, "EV6": 14, "EV7": 15, "EV8": 16, "EV9": 17, "EV10": 18, "EV11": 19, "EV12": 20, "EV13": 21, "EV14": 22, "EV15": 23, "EV16": 24, "EV17": 25, "EV18": 26, "EV19": 27, "EV20": 28, "EV21": 29, "EV22": 30, "EV23": 31}

class TCPServerMVR(protocol.Protocol, TimeoutMixin):
  
  def connectionMade(self):
    self.setTimeout(40)
    peer = self.transport.getPeer()
    self.ipAddr = peer.host
    self.port = peer.port
    logging.info("MVR: ip-> {}, port-> {}".format(peer.host, peer.port))
  
  def dataReceived(self, received):
    try: 
      connection = psycopg2.connect(user = conf['db']['user'], password = conf['db']['password'], host = conf['db']['host'], port = conf['db']['port'], database = conf['db']['database'])
      cursor = connection.cursor()
      strMsg = received.decode('utf-8')
      dataJson = json.loads(strMsg)
      baseInfo ={"version":dataJson["versionTrama"],"register_id":dataJson["idRegistro"],"client":dataJson["idOperador"],"vehicle_internal_code":dataJson["idVehiculo"],"lane_code":dataJson["idRuta"],"operator_internal_id":dataJson["idConductor"],"event_ocurrence":dataJson["fechaHoraLecturaDato"],"sharing_time":dataJson["fechaHoraEnvioDato"],"vehicle_kind":dataJson["tipoBus"],"localization":json.dumps(dataJson["localizacionVehiculo"]),"message_kind":dataJson["tipoTrama"],"motor_tech":dataJson["tecnologiaMotor"],"retransmited":dataJson["tramaRetransmitida"],"brake_kind":dataJson["tipoFreno"]}
      if ("codigoAlarma" in dataJson):
        baseInfo["event_kind"] = dataJson["codigoAlarma"]
        self.handleAlarms(cursor, connection, baseInfo, dataJson)
      elif ("codigoEvento" in dataJson):
        baseInfo["event_kind"] = dataJson["codigoEvento"]
        self.handleEvents(cursor, connection, baseInfo, dataJson)
      else:
        self.handlePeriodicReports(cursor, connection, baseInfo, dataJson)
    except Exception as e:  
      logging.error("Failed fam!: {}".format(e))
    finally:
      if(connection):
        cursor.close()
        connection.close()
    self.resetTimeout()

  def handleAlarms(self, cursor, connection, baseInfo, dataJson):
    try : 
      if dataJson["codigoAlarma"] == "ALA1" or dataJson["codigoAlarma"] == "ALA2" or dataJson["codigoAlarma"] == "ALA7":
        baseInfo["vehicle_acc"] = dataJson["aceleracionVehiculo"]
      elif dataJson["codigoAlarma"] == "ALA3":
        baseInfo["vehicle_speed"] = dataJson["velocidadVehiculo"]
      elif dataJson["codigoAlarma"] == "ALA4":
        baseInfo["weight"] = dataJson["peso"]
      elif dataJson["codigoAlarma"] == "ALA6":
        baseInfo["camera_code"] = dataJson["codigoCamara"]
      self.saveOnDb(cursor, connection, baseInfo)
    except Exception as error:
      logging.error("Failed to parse: {}".format(error))

  def handleEvents(self, cursor, connection, baseInfo, dataJson):
    try:
      if dataJson["codigoEvento"] == "EV1":
        baseInfo["weight"] = dataJson["peso"]
        baseInfo["cabin_temperature"] = dataJson["temperaturaCabina"]
        baseInfo["occupancy"] = dataJson["estimacionOcupacion"]
      elif dataJson["codigoEvento"] == "EV2":
        baseInfo["door_status"] = dataJson["estadoAperturaCierrePuertas"]
      elif dataJson["codigoEvento"] == "EV3":
        baseInfo["ventilation_system_status"] = dataJson["estadoSistemaVentilacion"]
      elif dataJson["codigoEvento"] == "EV4":
        baseInfo["light_system_status"] = dataJson["estadoSistemaIluminacion"]
      elif dataJson["codigoEvento"] == "EV5":
        baseInfo["windshield_wipers_status"] = dataJson["estadoSistemaLimpiaParabrisas"]
      self.saveOnDb(cursor, connection, baseInfo)
    except Exception as error:
      logging.error("Failed to parse: {}".format(error))

  def handlePeriodicReports(self, cursor, connection, baseInfo, dataJson):
    try: 
      if not ("temperaturaMotor" in dataJson):
        baseInfo["event_kind"] = "P20"
        baseInfo["vehicle_speed"] = dataJson["velocidadVehiculo"]
        baseInfo["vehicle_acc"] = dataJson["aceleracionVehiculo"]
      else: 
        baseInfo["event_kind"] = "P60"
        baseInfo["motor_temperature"]  = dataJson["temperaturaMotor"]
        baseInfo["oil_pressure"]  = dataJson["presionAceiteMotor"]
        baseInfo["rpm"]  = dataJson["revolucionesMotor"]
        baseInfo["break_status"]  = dataJson["estadoDesgasteFrenos"]
        baseInfo["km_odometer"]  = dataJson["kilometrosOdometro"]
        baseInfo["vehicle_consumption"]  = dataJson["consumoCombustible"]
        baseInfo["gas_level"]  = dataJson["nivelTanqueCombustible"]
        baseInfo["energy_consumption_level"]  = dataJson["consumoEnergia"]
        baseInfo["energy_regeneration_level"]  = dataJson["regeneracionEnergia"]
        baseInfo["energy_level"]  = dataJson["nivelRestanteEnergia"]
        baseInfo["percentage_generated_energy"]  = dataJson["porcentajeEnergiaGenerada"]
        baseInfo["course"]  = dataJson["sentidoMarcha"]
      self.saveOnDb(cursor, connection, baseInfo)
    except Exception as error:
      logging.error("Failed to parse: {}".format(error))

  def saveOnDb(self, cursor, connection, baseInfo):
    table = 'mvr_tms_messages'
    columns = list(baseInfo.keys())
    values  = list(baseInfo.values())
    query_string = sql.SQL("INSERT INTO {} ({}) VALUES {}").format(
      sql.Identifier(table),
      sql.SQL(', ').join(map(sql.Identifier, columns)),
      sql.SQL(', ').join(sql.Placeholder()*len(values)),
      ).as_string(cursor)
    final_query = cursor.mogrify(query_string, values)
    print(final_query)
    cursor.execute(final_query)
    connection.commit()

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