#
import sys
import paho.mqtt.client as mqtt
import time
import json
import random
import socket
import codecs


show_mesg = [
"=20180822= V2, 1.call on_message 2.TCP bridge  ",
"=20180822= V1, init ",
"***^^ What's new *****",
]



# MQTT Config 2

dataChnId1 = "Temperature"
MQTT_SERVER = "broker.mqttdashboard.com"  
MQTT_PORT = 1883  #1883 : MQTT, unencrypted
MQTT_ALIVE = 60  
MQTT_TOPIC1 = "testtopic/99"
MQTT_TOPIC1 = "testtopic/#"
MQTT_TOPIC1 = "test99/2.122.502.0.40101.in" 

'''
1883 : MQTT, unencrypted
8883 : MQTT, encrypted
8884 : MQTT, encrypted, client certificate required
8080 : MQTT over WebSockets, unencrypted
8081 : MQTT over WebSockets, encrypted
'''

OPT_SUBCR_WAIT = 5 # wait .. sec
OPT_MQTT_TOPICOUT = "test99/2.122.502.0.40101.out"


CONFIG_NET_HOST = '127.0.0.1'    # The local host
CONFIG_NET_PORT = 5002
CONFIG_Max_socket_getdata_wait = 1.5

# *********************************************************************
def proc_up(userdata):
    #resp=userdata.upper()
    print('got new')
    obj = json.loads(userdata)     
    print('tag: ' + str(obj['tag']))
    print('data: ' + str(obj['data']))
    #resp = str(obj['data'])
    if len(str(obj['data'])) > 0:
        resp = sendhex_and_closed(str(obj['data']))
        return resp

    
    
def on_message(client, userdata,msg):
    vdata = proc_up(msg.payload.decode("utf-8", "strict"))
    if len(vdata) >0:
        fire_pub(vdata)
        print(vdata)

    

def on_connect(self, client, userdata, rc):
    print("MQTT Connected.")
    self.subscribe(MQTT_TOPIC1)


def fire_pub(userdata):
    client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)
    client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)
    client.publish(OPT_MQTT_TOPICOUT,userdata,qos=2, retain=False)
    time.sleep(0.5)
    
def get_subcr_onetime():
    print("Try connect server..")
    print("Config :: MQTT_SERVER : " + str(MQTT_SERVER) \
          + " MQTT_PORT: " + str(MQTT_PORT) \
          + " MQTT_TOPIC1: " + str(MQTT_TOPIC1) )
    
    client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)
    ##client.loop_forever()
    client.loop_start()
    print('wait..' + str(OPT_SUBCR_WAIT) )
    time.sleep(OPT_SUBCR_WAIT) #wait 3s
    client.disconnect()
    print('!!discon')
    client.loop_stop()
    print('!!stop..')
    time.sleep(0.5)
    
    #fire_pub("999.225.455")

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
    #fire_pub("999.225.455.abc.def")
    
def sendhex_and_closed(message):
    # Echo client program


    
    HOST = CONFIG_NET_HOST
    PORT = CONFIG_NET_PORT

    data =''
    
    print('\r\nServer',HOST ,':', PORT )
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    try:
        s.connect((HOST, PORT))
        #s.sendall(message.encode())
        binary_data = codecs.decode(message, "hex_codec")
        s.sendall(binary_data)
        #s.settimeout(0.3) #wait timeout 300ms
        s.settimeout(CONFIG_Max_socket_getdata_wait) #wait timeout 300ms
        #data = s.recv(1024).decode() # String
        data = s.recv(1024).hex().upper() # big-endian Hex
        
    except socket.error:
        #write error code to file
        print('\r\ns.error')
        
    finally:
        s.close()
            
    if len(data)>0 :
        
        print( 'Received : ', data)
        
        data = json.dumps({
        'tag': '11/00',
        'data': data
        })
        
        print( 'Received JSON: ', data)
        
        
        
    return data


if __name__ == '__main__':
    
    for (i, msg) in enumerate(show_mesg):
        print(msg)
    
    #sendtext_and_closed("Hello")
    #sendhex_and_closed("48656C6C6F") # Hello
    fire_pub("999.225.455.abc.def")
    
    #get_subcr_onetime()
    get_subcr_forever()
    
    print('Call sys.exit()')
    sys.exit() #Exit
    
    
'''
import paho.mqtt.client as mqtt
host = "broker.mqttdashboard.com"
port = 8000
client = mqtt.Client()
client.connect(host)
client.publish("TEST/MQTT","HELLO MQTT")


{"tag": "11", "data": "313233"}

usage = json.dumps({
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'swap_percent': psutil.swap_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'net_fds': len(psutil.net_connections()),
        'pids': len(psutil.pids()),
        "opt_siml":"False",
        'id': nickname
        })
        

{"cpu_percent": 6.4, "memory_percent": 42.7, "swap_percent": 46.6, "disk_percent": 45.0, "net_fds": 165, "pids": 193, "opt_siml": "False", "id": "fBFJzYiQ-pK8k-mPLg-TgrN-CDFLjjpwBQQt"}
status: succeed
{"cpu_percent": 29.4, "memory_percent": 42.7, "swap_percent": 46.6, "disk_percent": 45.0, "net_fds": 166, "pids": 193, "opt_siml": "False", "id": "fBFJzYiQ-pK8k-mPLg-TgrN-CDFLjjpwBQQt"}


 # Example print:
        #   {"message": "success", "iss_position": {"longitude": "24.8002", "latitude": "-25.0600"}, "timestamp": 1565926321}  

        #obj = json.loads(res.text)     
        #print('message: ' + str(obj['message']))
        #print('Lon: ' + str(obj['iss_position']['longitude']))
        #print('Lat: ' + str(obj['iss_position']['latitude']))
        #print( 'timestamp: ' + str(obj['timestamp']))       
        
        # Example prints:
        #   1364795862
        #   -47.36999493 151.738540034


2019-08-22 14:27:37
Topic: test99/2.122.502.0.40101.out
Qos: 2
{"tag": "11/00", "data": "48454C4C4F2121"}
2019-08-22 14:27:36
Topic: test99/2.122.502.0.40101.in
Qos: 0
{"tag": "11", "data": "48656C6C6F"}
2019-08-22 14:27:25
Topic: test99/2.122.502.0.40101.in
Qos: 0
{"tag": "11", "data": "48656C6C6F"}


'''