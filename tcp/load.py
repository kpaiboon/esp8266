import sys
import os
import time
import socket
import json
import binascii
import paho.mqtt.client as mqtt
import datetime
import threading

from uuid import getnode as get_mac

import config as conf

VERSION_MAINPROG = 'V2.01--20191928--clean--win32'
show_mesg = [
VERSION_MAINPROG,
'V1.02--20191923--rm--win32'
'=20190916= V0.1 minimal print mqtt subscribe log',  
'***^^ What\'s new *****',
]


# MQTT Config 2
MQTT_SERVER = conf.CMQTT_SERVER
#MQTT_SERVER = "45.63.107.108"  
MQTT_PORT = conf.CMQTT_PORT  #1883 : MQTT, unencrypted
MQTT_ALIVE = conf.CMQTT_ALIVE  

MQTT_PUBSUBBROADCAST_TOPIC0 = conf.CMQTT_PUBSUBBROADCAST_TOPIC0 # or "" null
#MQTT_PUBSUBBROADCAST_TOPIC0 = 'test66#'

MQTT_SUBTOPIC1 = conf.CMQTT_SUBTOPIC1
MQTT_PUBTOPIC = conf.CMQTT_PUBTOPIC

mac_int = get_mac()
mac_hex = hex(mac_int)[2:] # hex(x)[2:] use hex() without 0x get the
CLIENT_ID = mac_hex[-6:].upper() #LAST 6-CHAR
print(CLIENT_ID)

MQTT_SUBTOPIC1 = MQTT_SUBTOPIC1.replace('{.CID}', CLIENT_ID, 2) # replace {.CID} ClientID
MQTT_PUBTOPIC = MQTT_PUBTOPIC.replace('{.CID}', CLIENT_ID, 2) # replace {.CID} ClientID

print(MQTT_PUBSUBBROADCAST_TOPIC0)
print(MQTT_SUBTOPIC1)
print(MQTT_PUBTOPIC)

TYPE_REBOOT = 'call_coredevicereboot({.CID})'
TYPE_REBOOT = TYPE_REBOOT.replace('{.CID}', CLIENT_ID, 2) # replace {.CID} ClientID
PATTERN_REBOOT5M = 'reset_5m'
PATTERN_REBOOT3M = 'reset_3m'
PATTERN_REBOOT1M = 'reset_1m'

print(TYPE_REBOOT, PATTERN_REBOOT5M, PATTERN_REBOOT3M, PATTERN_REBOOT1M)

# *********************************************************************  
    
def on_message(client, userdata,msg):
    vdata = msg.payload.decode("utf-8", "strict")
    print("\r\nTimestamp= ",datetime.datetime.now(),", message topic= ",msg.topic ,", len= ",len(vdata))
    #print(vdata)  

    if ( '\"tag\"') in vdata:
        if not (( TYPE_REBOOT) in vdata):
            wdt_feed()
            print('Found tag')
            data = RTU_poll(vdata)
            if len(data) >=2:
                print(MQTT_PUBTOPIC)
                client.publish(MQTT_PUBTOPIC,data)
        else:
            if( PATTERN_REBOOT5M)in vdata:
                wdt_autoreboot(5)
            if( PATTERN_REBOOT3M)in vdata:
                wdt_autoreboot(3)
            if( PATTERN_REBOOT1M)in vdata:
                wdt_autoreboot(1)

def on_connect(self, client, userdata, rc):
    print("MQTT Connected.")
    #self.subscribe(MQTT_TOPIC1)
    print(MQTT_SUBTOPIC1)
    mysubtopic = [MQTT_SUBTOPIC1]
    if MQTT_PUBSUBBROADCAST_TOPIC0 !='':
        print('Dbg: bc')
        print(MQTT_PUBSUBBROADCAST_TOPIC0)
        mysubtopic = [MQTT_SUBTOPIC1,MQTT_PUBSUBBROADCAST_TOPIC0]

    print(mysubtopic)
    self.subscribe(MQTT_PUBSUBBROADCAST_TOPIC0)


client = mqtt.Client(client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv31)  
def get_subcr_forever():
    global client
    print("Try connect server..")
    print("Config :: MQTT_SERVER : " + str(MQTT_SERVER) \
          + " MQTT_PORT: " + str(MQTT_PORT) )    
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)
    pcproc_helloPub()

    print("Try loop_forever..")
    client.loop_forever()
    
def pcproc_helloPub():
    global client
    jdata = json.dumps({
    'dev':'Dummy',
    'platform': '{}'.format(sys.platform.upper().replace(' ', '_')),
    'ticks_ms': '{}'.format(str(int(time.time_ns()/1000))), #time_ns/1000 to ticks_ms ##fix cross WIN32
    'ifconfig_ip': '{}'.format(str(socket.gethostbyname(socket.gethostname()))), ##fix cross WIN32
    'halfid': '{}'.format(CLIENT_ID),
    'file__main.py_sizebyte': '{}'.format( str(os.stat('load.py')[6] )),
    'file__config.py_sizebyte': '{}'.format( str(os.stat('config.py')[6] )),
    'main_ver': '{}'.format( str(VERSION_MAINPROG)),
    })
    print(jdata)
    print(MQTT_PUBTOPIC)
    client.publish(MQTT_PUBTOPIC, jdata)

def pcifsendhex_and_closed(message, txt_ip, txt_port, txt_waitrecv):
    ##  s.settimeout(Float_waitrecv) #MUST after setting proto
    Int_port = int(txt_port)
    Float_waitrecv = float(txt_waitrecv)

    data = ''    
    print ('\r\nServer', txt_ip, ':', str(Int_port))
    
    try:
        binary_data = binascii.unhexlify(message)
        #print(binary_data)
        print ('Check Input HEX: ' + str(binascii.hexlify(binary_data)).upper())       
    except:
        print ('\r\nbinascii.err')
        return ''
        
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(Float_waitrecv) #wait timeout 300ms
        s.connect((txt_ip, Int_port))
        s.sendall(binary_data)
        data = s.recv(1024)
        
    except socket.error as e:
        print ('\r\ns.err')
        
    finally:
        s.close()

    if len(data) > 0:
        print ('Received : ', str(data) + ' len = ' + str(len(data)))  # #fix cross WIN32
        # #print(str(data))
        data = str(binascii.hexlify(data)).upper()
        # #print(data)
        data = data.replace('B\'', '')
        data = data.replace('b\'', '')
        data = data.replace('\'', '')
        # print(data)
        print ('Received HEX: ', data + ' len = ' + str(len(data))
               + ' len/2 = ' + str(len(data) / 2))
        # data = json.dumps({'tag': '11/00','data': data})
        # print( 'Received JSON: ', data)
        # print(data)

    return data

def RTU_poll(jmessage):

  # return '' if false
  # return data if process ok

    my_intype = ''
    my_message = ''
    my_txt_ip = ''
    my_txt_port = ''
    my_txt_waitrecv = ''

    print ('RTU_poll running')
    #print (jmessage)
    try:
        json_object = json.loads(jmessage)
    except ValueError as e:
        print ('JSON input err')
        return ''
    print (json_object)

    try:
        my_intype = json_object['type']
        my_message = json_object['data']
        my_txt_ip = json_object['ipd']
        my_txt_port = json_object['portd']
        my_txt_waitrecv = json_object['waitresp']
        # debug
        print (my_intype, my_message, my_txt_ip, my_txt_port,
               my_txt_waitrecv)
    except KeyError as e:

        print ('JSON Get Key 1 err')
        return ''

    if my_intype == 'raw_hex':
        # ifsendhex_and_closed("3132330D0A","192.168.10.150","5021","2")
        data = pcifsendhex_and_closed(my_message, my_txt_ip, my_txt_port,my_txt_waitrecv)
    else:
        print ('Incorrect type of operation')
        return ''

    json_object['ticks_ms'] = str(int(time.time_ns() / 1000))  # time_ns/1000 to ticks_ms ##fix cross WIN32
    json_object['ifconfig_ip'] = \
        str(socket.gethostbyname(socket.gethostname()))  # #fix cross WIN32

    if len(data) >= 2:
        json_object['type'] = json_object['type'] + '__resp'  # mod type resp
        json_object['data_resp'] = data  # add data_resp
    else:
        json_object['type'] = json_object['type'] + '__TimeoutError'  # mod type resp

    data = json.dumps(json_object)
    print (data)
    return data


def wdt_feed():
    global wdt_counter
    wdt_counter = 0
    print('Dbg: call wdt_f()')

def wdt_autoreboot(n):
    global wdt_counter_autosoftreboot
    print('Dbg: call wdt_ar()')
    if(n>=1):
        wdt_counter_autosoftreboot = n+1
        print('n+1 : ' + str(wdt_counter_autosoftreboot))
    else:
        wdt_counter_autosoftreboot = 0
        print('Dis: wdt_counter_autosoftreboot = 0')

## Simple software WDT implementation
print('\n\r\nPreparing Watchdog\r\n') 
wdt_onedayrebootminute = 29 # 0 or one day reboot in 55 minute
wdt_upperlimitminute = 10 # 0 or watchdog reboot in 10 minute

#wdt_onedayrebootminute = 0 # 0 or one day reboot in 55 minute
#wdt_upperlimitminute = 0 # 0 or watchdog reboot in 10 minute

print('!!wdt s-->: ' , ' 0 disable or  wdt_onedayrebootminute ' , wdt_onedayrebootminute )
print('!!wdt s-->: ' , ' 0 disable or  wdt_upperlimitminute ' , wdt_upperlimitminute )
time.sleep(5)
wdt_counter_oneday = 0
wdt_counter = 0
wdt_counter_autosoftreboot = 0 # 0 or soft reboot 3 minute

def wdt_callback():
    global wdt_counter_oneday
    global wdt_counter
    global wdt_wlancounter
    global wdt_counter_autosoftreboot
    wdt_counter_oneday += 1
    wdt_counter += 1

  
    if (wdt_counter_oneday >= wdt_onedayrebootminute) and  ( wdt_onedayrebootminute !=0):
        print('\n\r\n !!wdt..r..one-day..')
        #machine.reset()
        print('Call os._exit(0)')
        os._exit(0) #force exit
    
    if (wdt_counter >= wdt_upperlimitminute) and  ( wdt_upperlimitminute !=0):
        print('\n\r\n !!wdt..r..now')
        #machine.reset()
        print('Call os._exit(0)')
        os._exit(0) #force exit
    
    if (wdt_counter >= (wdt_upperlimitminute*0.5)) and  ( wdt_upperlimitminute !=0):
        print('\n\r\n !!wdt..> 50%')
  
    if (wdt_counter_autosoftreboot !=0):  
        if(wdt_counter_autosoftreboot >0):
            wdt_counter_autosoftreboot = wdt_counter_autosoftreboot -1
      
        print('\n\r\n !!auto..r..act\r\n >: ' + str(wdt_counter_autosoftreboot))
        if (wdt_counter_autosoftreboot <= 1):
            print('\n\r\n !!auto..r..now\r\n')
            #machine.reset()
            print('Call os._exit(0)')
            os._exit(0) #force exit
  
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
        work(self.number, self.listcmd, self.logger)



def work(number,listcmd, logger):
    """
    A function that can be used by a thread
    """
    #print("Timer1")
    print('\r\n' + threading.currentThread().getName() + '\r\n')
    while True:
        start = time.time_ns()
        to = 60 *1000*1000*1000 # 60 x [1000,000,000 ns]
        time.sleep(1)
        while (time.time_ns()- start) < to:
            time.sleep(0.5)
        #print("Timer armed")
        wdt_callback()
        time.sleep(0.5)
        
  
  
if __name__ == '__main__':   
    for (i, msg) in enumerate(show_mesg):
        print(msg)
    
    #sendtext_and_closed('CCAABBCC', '192.168.10.50', '502', '1.4')
    #sendtext_and_closed('CC11AABBCC', '192.168.10.50', '502', '1.4')
    
    #pcifsendhex_and_closed('xxxAABBCC', '192.168.10.50', '502', '1.4')
    #pcifsendhex_and_closed('11AABBCC', '192.168.10.50', '502', '1.4')
    #pcifsendhex_and_closed('99AABBCC', '192.168.10.50', '502', '1.4')
    
    i =1
    j =2
    k =3
    thread = MyThread(i,j, k)
    thread.setName("Timer1")
    thread.start()
    
    

    
    #get_subcr_onetime()
    get_subcr_forever()
    
    print('Call sys.exit()')
    #sys.exit() #Exit
    os._exit(0) #force exit
