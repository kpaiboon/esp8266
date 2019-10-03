#use: import config as conf
_version = '0.2--20190930--config_mqtt__topic'
#_version = '0.1--20190927--new_mqtt__config'

#main.py config

CMQTT_SERVER = 'broker.mqttdashboard.com'  
CMQTT_PORT = 1883  #1883 : MQTT, unencrypted
CMQTT_ALIVE = 5*60  # def 15 mins

CMQTT_PUBSUBBROADCAST_TOPIC0 = 'bems/sta99/dev/broadcast/#' # or "" null
CMQTT_SUBTOPIC1 = 'bems/sta99/dev/u/N_{.CID}/dl' 
CMQTT_PUBTOPIC = 'bems/sta99/dev/u/N_{.CID}/up'


'''
1883 : MQTT, unencrypted
8883 : MQTT, encrypted
8884 : MQTT, encrypted, client certificate required
8080 : MQTT over WebSockets, unencrypted
8081 : MQTT over WebSockets, encrypted
'''



