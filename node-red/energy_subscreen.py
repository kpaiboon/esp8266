import sys
import paho.mqtt.client as mqtt
import datetime
import json
import binascii
import struct

VERSION_MAINPROG = 'V0.32--20190930--config-mqtt-topic'

show_mesg = [
VERSION_MAINPROG,
'V0.32--20190927--locate-bems',
'V0.31--20190923--{}.format()',
'V0.30--20190922--print 5 value',
"=20190921= V0.3 subscreen",  
"=20190921= V0.2 decode tag modbus",  
"=20190916= V0.1 minimal print mqtt subscribe log",  
"***^^ What's new *****",
]

# MQTT Config 2
MQTT_SERVER = "broker.mqttdashboard.com"  
MQTT_PORT = 1883  #1883 : MQTT, unencrypted
MQTT_ALIVE = 600  

MQTT_PUBSUBBROADCAST_TOPIC0 = "test99/broadcast/#" # or "" null
MQTT_PUBSUBBROADCAST_TOPIC0 = "test99/#" # or "" null
MQTT_PUBSUBBROADCAST_TOPIC0 =''

MQTT_SUBTOPIC1 = "test99/pow101/dev/u/#" 
MQTT_SUBTOPIC1 = "test99/pow101/matrix/screen101"
MQTT_SUBTOPIC1 = "bems/sta99/pwr/scn/dp1" 

#MQTT_PUBTOPIC = "test99/pow101/matrix/screen101"

client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)

'''
1883 : MQTT, unencrypted
8883 : MQTT, encrypted
8884 : MQTT, encrypted, client certificate required
8080 : MQTT over WebSockets, unencrypted
8081 : MQTT over WebSockets, encrypted
'''
# *********************************************************************  


def decode_pow_screen(jmessage):
    try:
        json_object = json.loads(jmessage)
    except ValueError as e:
        print("JSON input error")
        return ''
        
    #print(json_object)
    try:
        my_txt_tag = json_object["tag"]
        my_intype = json_object["type"]
        my_txt_ip = json_object["ipd"]
        my_mbtcp_listregval_txtfloat = json_object["mbtcp_listfloat32"]
        my_mbtcp_listregval_txtu16 = json_object["mbtcp_listu16"]
        
        my_mbtcp_reshexatransid = json_object["mbtcp_reshexatransid"] 
        my_mbtcp_reshexafunc = json_object["mbtcp_reshexafunc"]
        my_mbtcp_hexastartaddr = json_object["mbtcp_hexastartaddr"] 
        my_mbtcp_resintbyteqty = json_object["mbtcp_resnumbyteqty"]
        
        #debug
        #print(my_txt_tag,my_intype,my_mbtcp_listregval_txtfloat)
        print(my_txt_tag,my_intype,my_txt_ip,my_mbtcp_reshexatransid,my_mbtcp_reshexafunc,my_mbtcp_hexastartaddr,str(int(int(my_mbtcp_resintbyteqty))))
    except KeyError as e:
        print("JSON Get Key 1 error")
        return ''

    print('')
    for (i,txt) in enumerate(my_mbtcp_listregval_txtu16):
        if ((i+1)%10 ==0):
            #print((i*1)+1,txt)
            print('{:02d} {:05d}'.format((i*1)+1,int(txt)))
        else:
            #print((i*1)+1,txt,'\t',end = '') #,end='' no newline
            print('{:02d} {:05d}\t'.format((i*1)+1,int(txt)),end='') #,end='' no newline
    print('\r\n')
    
    #print('')
    for (i,txt) in enumerate(my_mbtcp_listregval_txtfloat):
        if ((i+1)%5 ==0):
            #print((i*2)+1,':',txt)
            print('{:02d}:{:.5g}'.format((i*2)+1,float(txt)))
        else:
            #print((i*2)+1,':',txt,'\t',end = '') #,end='' no newline
            print('{:02d}:{: 9.5g}\t\t'.format((i*2)+1,float(txt)),end = '') #,end='' no newline
    print('\r\n')    
            
            
        
    
def on_message(client, userdata,msg):
    #print("Timestamp>>= ",datetime.datetime.now())
    #print("message topic>>= ",msg.topic)
    vdata = msg.payload.decode("utf-8", "strict")
    print("\r\nTimestamp= ",datetime.datetime.now(),", message topic= ",msg.topic ,", len= ",len(vdata))
    #print(vdata)
    decode_pow_screen(vdata)

    

def on_connect(self, client, userdata, rc):
    print("MQTT Connected.")
    print("New session being set up")
    print(MQTT_SERVER)
    print(MQTT_SUBTOPIC1)
    self.subscribe(MQTT_SUBTOPIC1)
  
    if MQTT_PUBSUBBROADCAST_TOPIC0 !="":
        print("Debug MQTT_PUBSUBBROADCAST_TOPIC0 or test99/#")
        print(MQTT_PUBSUBBROADCAST_TOPIC0)
        self.subscribe(MQTT_PUBSUBBROADCAST_TOPIC0) #add Multiple topic

def get_subcr_forever():
    global client
    print("Try connect server..")
    print("Config :: MQTT_SERVER : " + str(MQTT_SERVER) \
          + " MQTT_PORT: " + str(MQTT_PORT) \
          + " MQTT_SUBTOPIC1: " + str(MQTT_SUBTOPIC1) )
    
    #client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)
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
