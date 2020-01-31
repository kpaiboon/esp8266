import sys
import paho.mqtt.client as mqtt
import datetime

show_mesg = [
"=20190916= V0.1 minimal print mqtt subscribe log",  
"***^^ What's new *****",
]

# MQTT Config 2
MQTT_SERVER = "broker.mqttdashboard.com"
MQTT_PORT = 1883  #1883 : MQTT, unencrypted
MQTT_ALIVE = 600  

MQTT_TOPIC1 = "test99/#"

'''
1883 : MQTT, unencrypted
8883 : MQTT, encrypted
8884 : MQTT, encrypted, client certificate required
8080 : MQTT over WebSockets, unencrypted
8081 : MQTT over WebSockets, encrypted
'''
# *********************************************************************  
    
def on_message(client, userdata,msg):
    #print("Timestamp>>= ",datetime.datetime.now())
    #print("message topic>>= ",msg.topic)
    vdata = msg.payload.decode("utf-8", "strict")
    print("\r\nTimestamp= ",datetime.datetime.now(),", message topic= ",msg.topic ,", len= ",len(vdata))
    print(vdata) 

def on_connect(self, client, userdata, rc):
    print("MQTT Connected.")
    self.subscribe(MQTT_TOPIC1)

def get_subcr_forever():
    print("Try connect server..")
    print("Config :: MQTT_SERVER : " + str(MQTT_SERVER) \
          + " MQTT_PORT: " + str(MQTT_PORT) \
          + " MQTT_TOPIC1: " + str(MQTT_TOPIC1) )
    
    client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)
    print("Try loop_forever..")
    client.loop_forever()

if __name__ == '__main__':   
    for (i, msg) in enumerate(show_mesg):
        print(msg)
    
    #get_subcr_onetime()
    get_subcr_forever()
    
    print('Call sys.exit()')
    sys.exit() #Exit
