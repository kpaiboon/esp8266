import sys
import paho.mqtt.client as mqtt
import datetime
import json
import binascii
import struct
import threading
import time


VERSION_MAINPROG = 'V0.32--20190930--config-mqtt-topic'

show_mesg = [
VERSION_MAINPROG,
'V0.32--20190927--locate-bems',
'V0.31--20190922--fixed float 8 digit--add--uint16--mbtcp_listfloat32--mbtcp_listu16',
'=20190921= V0.2 decode tag modbus',  
'=20190916= V0.1 minimal print mqtt subscribe log',  
'***^^ What\'s new *****',
]

# MQTT Config 2
MQTT_SERVER = "broker.mqttdashboard.com"
MQTT_PORT = 1883  #1883 : MQTT, unencrypted
MQTT_ALIVE = 600  

#MQTT_PUBSUBBROADCAST_TOPIC0 = "test99/broadcast/#" # or "" null
#MQTT_PUBSUBBROADCAST_TOPIC0 = "test99/#" # or "" null
MQTT_PUBSUBBROADCAST_TOPIC0 =''


MQTT_SUBTOPIC1 = "bems/sta99/dev/u/#" 

MQTT_PUBTOPIC = "bems/sta99/pwr/scn/dp1"

MQTT_PUBTOPIC_AUTOGEN = "bems/sta99/dev/broadcast/1"
MQTT_PUBTOPIC_AUTOGEN_timeinterval = 5 # 10sec

automsg1 = '''{"tag": "11/04", "type": "raw_hex", "data": "000300000006010400000064","ipd": "192.168.10.50","portd": "502", "waitresp": "1.4"}'''



client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)

'''
1883 : MQTT, unencrypted
8883 : MQTT, encrypted
8884 : MQTT, encrypted, client certificate required
8080 : MQTT over WebSockets, unencrypted
8081 : MQTT over WebSockets, encrypted
'''
# *********************************************************************  

def decode_RTU_poll(jmessage):
    '''
    {"tag": "11/04", "data": "000300000006010400000064",
    "ipd": "192.168.10.50", "ifconfig_ip": "192.168.10.71",
    "data_resp": "0003000000CB0104C843647D550000000000000000
    3D87B8A0000000000000000000000000000000000000000041718C4
    00000000000000000C1708AC300000000000000003DBAA6653F800000
    3F800000C2A98DEB0000000000000000429F5D64000000003D8E05CE3E5508B5
    00000000000000000000000041718C4000000000C1708AC33DBB071B00000000
    C2A9887C000000004247F38D3FB6A7F0000000003D54FDF43F6F1AA03FDE046D411E89EB
    0000000042CE333B000000000000000000000000000000000000000000000000",
    "portd": "502", "waitresp": "1.4", "ticks_ms": "1609206", "type": "raw_hex__resp"}
    '''
    #print(jmessage)
    try:
        json_object = json.loads(jmessage)
    except ValueError as e:
        print("JSON input error")
        return ''
    
    print(json_object)
    try:
        my_txt_tag = json_object["tag"]
        my_intype = json_object["type"]
        my_mbtcp_req = json_object["data"]
        my_mbtcp_res = json_object["data_resp"]
        my_txt_ip = json_object["ipd"]
        my_txt_port = json_object["portd"]
        my_txt_waitrecv = json_object["waitresp"]
        #debug
        print(my_txt_tag,my_intype,my_mbtcp_req,my_mbtcp_res,my_txt_ip,my_txt_port,my_txt_waitrecv)
    except KeyError as e:
        print("JSON Get Key 1 error")
        return ''  
    #000300000006010400000064 
    if len(my_mbtcp_req) == (12*2) :
        my_mbtcp_hexatransid = my_mbtcp_req[0:4]
        my_mbtcp_hexaprotoid = my_mbtcp_req[4:8]
        my_mbtcp_hexatcplen = my_mbtcp_req[8:12]
        my_mbtcp_hexauid = my_mbtcp_req[12:14]
        my_mbtcp_hexafunc = my_mbtcp_req[14:16]
        my_mbtcp_hexastartaddr = my_mbtcp_req[16:20]
        my_mbtcp_hexaqty = my_mbtcp_req[20:24]
        my_mbtcp_intqty = int(int(my_mbtcp_hexaqty,16))
        #debug
        print(my_mbtcp_req)
        print(my_mbtcp_hexatransid,my_mbtcp_hexaprotoid,\
              my_mbtcp_hexatcplen,my_mbtcp_hexauid,my_mbtcp_hexafunc,\
              my_mbtcp_hexastartaddr,my_mbtcp_hexaqty)
        print(my_mbtcp_intqty)
    else:
        print("my_mbtcp_req sz err")
        return ''
    
    if len(my_mbtcp_res) >= (9*2) :
        my_mbtcp_reshexatransid = my_mbtcp_res[0:4]
        my_mbtcp_reshexaprotoid = my_mbtcp_res[4:8]
        my_mbtcp_reshexatcplen = my_mbtcp_res[8:12]
        my_mbtcp_reshexauid = my_mbtcp_res[12:14]
        my_mbtcp_reshexafunc = my_mbtcp_res[14:16]
        my_mbtcp_reshexabyteqty = my_mbtcp_res[16:18]
        my_mbtcp_resintbyteqty = int(int(my_mbtcp_reshexabyteqty,16)/2)
        #debug
        print(my_mbtcp_res)
        print(my_mbtcp_reshexatransid,my_mbtcp_reshexaprotoid,\
              my_mbtcp_reshexatcplen,my_mbtcp_reshexauid,my_mbtcp_reshexafunc,\
              my_mbtcp_reshexabyteqty)
        print(my_mbtcp_resintbyteqty)
        
        my_mbtcp_resintfunc = int(my_mbtcp_reshexafunc,16)
        #my_mbtcp_resintfunc = int('F0',16)
        if (my_mbtcp_resintfunc >0) and (my_mbtcp_resintfunc < 127):
            print('Okay modbus response, code  = ',my_mbtcp_resintfunc)
            
            #float
            mloop = int(my_mbtcp_resintbyteqty/2)
            print('maxloop' + str(mloop))
            x = 0
            my_mbtcp_hexafloat32regval = []
            my_mbtcp_listtxtfloatregval = []
            while x < mloop:
                hexa = my_mbtcp_res[((9*2)+(x*8)):(((9*2)+(x*8))+8)]#get 8 char
                #print(x)
                #print(hexa)
                my_mbtcp_hexafloat32regval.append(hexa )
                
                #print fixed digit // but fail
                #>>> '{0:.9g}'.format(ff*ff*ff*ff*ff)
                #'4.47504186e-57'
                #>>> '{0:.8g}'.format(ff*ff*ff*ff*ff)
                #'4.4750419e-57'
                #>>> '{0:.7g}'.format(ff*ff*ff*ff*ff)
                #'4.475042e-57'
                #>>> ff
                #5.372289657158376e-12
                #txtfloat = str(struct.unpack('>f', binascii.unhexlify(hexa)))
                #txtfloat = txtfloat.replace("(", "")
                #txtfloat = txtfloat.replace(",)", "")
                
                txtflt = struct.unpack('>f', binascii.unhexlify(hexa))
                txtfloat = '{:.8g}'.format(float('{:.8g}'.format(txtflt[0])))
                #print(txtfloat)
                txtfloat = txtfloat.replace("(", "")
                txtfloat = txtfloat.replace(",)", "")
                #print(txtfloat)
                
                my_mbtcp_listtxtfloatregval.append(txtfloat)
                x = x +1
                

            #uint16
            mloop = int(my_mbtcp_resintbyteqty)
            print('maxloop' + str(mloop))
            x = 0
            my_mbtcp_hexau16regval = []
            my_mbtcp_listtxtu16regval = []
            while x < mloop:
                hexa = my_mbtcp_res[((9*2)+(x*4)):(((9*2)+(x*4))+4)]#get 4 char
                #print(x)
                #print(hexa)
                my_mbtcp_hexau16regval.append(hexa )
                
                txtu16 = str(struct.unpack('>H', binascii.unhexlify(hexa)))
                #print(txtu16)
                txtu16 = txtu16.replace("(", "")
                txtu16 = txtu16.replace(",)", "")
                #print(txtu16)
                my_mbtcp_listtxtu16regval.append(txtu16)
                x = x +1
                
            #print(my_mbtcp_hexafloat32regval)
            #print(my_mbtcp_hexau16regval)
            print(my_mbtcp_listtxtfloatregval)
            json_object["mbtcp_listfloat32"] = my_mbtcp_listtxtfloatregval
            
            print(my_mbtcp_listtxtu16regval)
            json_object["mbtcp_listu16"] = my_mbtcp_listtxtu16regval
            
        else:
            print('Illegal modbus response, exception code  = ',my_mbtcp_resintfunc)
               
    else:
        print("my_mbtcp_res sz err")
        return ''
    
    ## convert ready
    json_object["type"] = 'pow_matrix_screen' #type
    
    json_object["mbtcp_hexatransid"] = my_mbtcp_hexatransid
    json_object["mbtcp_hexafunc"] = my_mbtcp_hexafunc   
    json_object["mbtcp_hexastartaddr"] = my_mbtcp_hexastartaddr  
    json_object["mbtcp_numqty"] = str(my_mbtcp_intqty)
    
    json_object["mbtcp_reshexatransid"] = my_mbtcp_reshexatransid 
    json_object["mbtcp_reshexafunc"] = my_mbtcp_reshexafunc
    json_object["mbtcp_resnumbyteqty"] = str(my_mbtcp_resintbyteqty)
    
    
    
    data = json.dumps(json_object, sort_keys=True)
    
    
    return data


def on_message(client, userdata,msg):
    #print("Timestamp>>= ",datetime.datetime.now())
    #print("message topic>>= ",msg.topic)
    vdata = msg.payload.decode("utf-8", "strict")
    print("\r\nTimestamp= ",datetime.datetime.now(),", message topic= ",msg.topic ,", len= ",len(vdata))
    #print(vdata)
    if ( "\"tag\"") in vdata:
        print("Found tag")
        if ("raw_hex__resp") in vdata:
            data = decode_RTU_poll(vdata)
            print(data)
            client.publish(MQTT_PUBTOPIC,data)
    else: 
        print("no tag")

    

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
    

class MyThread(threading.Thread):
    
    def __init__(self, number, listcmd ,logger):
        threading.Thread.__init__(self)
        self.number = number
        self.logger = logger
        self.listcmd = listcmd
 
    def run(self):
        """
        Run the thread
        """
        #logger.debug('Calling worker')
        #logger.debug('.getname = ' + threading.currentThread().getName())
        #doubler(self.number, self.logger)
        work(self.number, self.listcmd, self.logger)

def work(number,listcmd, logger):
    """
    A function that can be used by a thread
    """
    #logger.debug('Work function executing')
    #__imei = threading.currentThread().getName()
    print("Timer1")
    
    while True:
        start = time.time_ns()
        to = MQTT_PUBTOPIC_AUTOGEN_timeinterval *1000*1000*1000 # 50 x [1000,000,000 ns]
        time.sleep(1)
        while (time.time_ns()- start) < to:
            time.sleep(0.5)
            
        print("Timer armed")   
        time.sleep(0.5)
        print('auto publish')
        client.publish(MQTT_PUBTOPIC_AUTOGEN,automsg1)
        
if __name__ == '__main__':   
    for (i, msg) in enumerate(show_mesg):
        print(msg)
    
    i =1
    j =2
    k =3
    thread = MyThread(i,j, k)
    thread.setName("Timer")
    thread.start()

    #get_subcr_onetime()
    get_subcr_forever()
    
    print('Call sys.exit()')
    sys.exit() #Exit
