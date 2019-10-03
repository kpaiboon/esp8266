#exec(open('./boot.py').read(),globals())
import sys
import os
import uos
import machine
import time
import ujson as json
import ubinascii as binascii
import socket
from umqtt_robust import MQTTClient

import config as conf


VERSION_MAINPROG = 'V1.03--20191930--set--tcptimeout.py'
#VERSION_MAINPROG = 'V1.02--20191927--add--load-config.py'
#VERSION_MAINPROG = 'V1.02--20191923--rm--win32'
#VERSION_MAINPROG = 'V1.01--20191923--add--WL_SSID'
#VERSION_MAINPROG = 'V0.99--20191920--add--filesize'

print('main2-esp32' + VERSION_MAINPROG)


# MQTT Config 2

MQTT_SERVER = conf.CMQTT_SERVER  
MQTT_PORT = conf.CMQTT_PORT  #1883 : MQTT, unencrypted
MQTT_ALIVE = conf.CMQTT_ALIVE  # def 15 mins

#MQTT_SERVER = "broker.mqttdashboard.com"  
#MQTT_PORT = 1883  #1883 : MQTT, unencrypted
#MQTT_ALIVE = 5*60  # def 15 mins

MQTT_PUBSUBBROADCAST_TOPIC0 = conf.CMQTT_PUBSUBBROADCAST_TOPIC0 # or "" null

#MQTT_PUBSUBBROADCAST_TOPIC0 = "test99/broadcast/#" # or "" null


MQTT_SUBTOPIC1 = conf.CMQTT_SUBTOPIC1
MQTT_PUBTOPIC = conf.CMQTT_PUBTOPIC

#MQTT_SUBTOPIC1 = "test99/2.122.502.0.40101/N_{.CID}/in" 
#MQTT_PUBTOPIC = "test99/2.122.502.0.40101/N_{.CID}/out"

try:
  CLIENT_ID = binascii.hexlify(network.WLAN().config('mac')).decode().upper()[-6:] #LAST 6-CHAR
except NameError:
  CLIENT_ID = "demo"


MQTT_SUBTOPIC1 = MQTT_SUBTOPIC1.replace('{.CID}', CLIENT_ID, 2) # replace {.CID} ClientID
MQTT_PUBTOPIC = MQTT_PUBTOPIC.replace('{.CID}', CLIENT_ID, 2) # replace {.CID} ClientID

print(MQTT_SUBTOPIC1)
print(MQTT_PUBTOPIC)


TYPE_REBOOT = 'call_coredevicereboot({.CID})'
TYPE_REBOOT = TYPE_REBOOT.replace('{.CID}', CLIENT_ID, 2) # replace {.CID} ClientID
PATTERN_REBOOT5M = 'reset_5m'
PATTERN_REBOOT3M = 'reset_3m'
PATTERN_REBOOT1M = 'reset_1m'

print(TYPE_REBOOT, PATTERN_REBOOT5M, PATTERN_REBOOT3M, PATTERN_REBOOT1M)

#  {"tag": "11/00", "type": "call_coredevicereboot(0A6AD0)", "data": "reset_3m"}


def sub_cb(topic, msg):
  print((topic, msg))
  
  if ( '\"tag\"') in msg:
    if not (( TYPE_REBOOT) in msg):
      wdt_feed()
      print('Found tag')
      data = RTU_poll(msg)
      if len(data) >=2:
        c.publish(MQTT_PUBTOPIC,data)
    else:
      if( PATTERN_REBOOT5M)in msg:
        wdt_autoreboot(5)
      if( PATTERN_REBOOT3M)in msg:
        wdt_autoreboot(3)
      if( PATTERN_REBOOT1M)in msg:
        wdt_autoreboot(1)  
 
  #wdt_feed()
  #Read F3 0001 c10
  #00 03 00 00 00 06 01 03 00 01 00 0A
#  mstring = '''{"tag": "11/00", "type": "raw_hex", "data": "00030000000601030001000A","ipd": "192.168.10.150","portd": "502", "waitresp": "1.4"}
#  '''
  
#  mstring = '''{"tag": "11/01", "type": "raw_hex", "data": "00030000000601030001000A","ipd": "192.168.10.150","portd": "502", "waitresp": "1.4"}
#{"tag": "11/02", "type": "raw_hex", "data": "000300000006010300010005","ipd": "192.168.10.150","portd": "502", "waitresp": "1.4"}
#{"tag": "11/03", "type": "raw_hex", "data": "000300000006010300010011","ipd": "192.168.10.150","portd": "502", "waitresp": "1.4"}
#{"tag": "11/04", "type": "raw_hex", "data": "000300000006010300010015","ipd": "192.168.10.150","portd": "502", "waitresp": "1.4"}
#'''

#{"tag": "11/00", "type": "call_coredevicereboot(0A6AD0)", "data": "reset_3m"}


led = machine.Pin(2, machine.Pin.OUT) #create LED ,Set Pin27 to output
LED_ASSERT = 0 # light on
LED_DEASSERT = 1 # light off

print('APP LED Blink ..')

def proc_helloPub():
  jdata = json.dumps({
  'dev':'Dummy',
  'version': '{}'.format(os.uname().version.replace(' ', '_')),
  'machine': '{}'.format(os.uname().machine.replace(' ', '_')),
  'platform': '{}'.format(sys.platform.upper().replace(' ', '_')),
  'ticks_ms': '{}'.format(time.ticks_ms()),
  'ifconfig_ip': '{}'.format( str(wlan.ifconfig()[0])),
  'ifconfig_ssid': '{}'.format(WL_SSID),
  'halfid': '{}'.format(CLIENT_ID),
  'file__main.py_sizebyte': '{}'.format( str(os.stat('/main.py')[6] )),
  'file__boot.py_sizebyte': '{}'.format( str(os.stat('/boot.py')[6] )),
  'main_ver': '{}'.format( str(VERSION_MAINPROG)),
  })
  print(jdata)
  c.publish(MQTT_PUBTOPIC, jdata)


def ifsendhex_and_closed(message,txt_ip,txt_port,txt_waitrecv):
  #ifsendhex_and_closed("3132330D0A","192.168.43.1","5021","2")
  # Echo client program 
  Int_port = int(txt_port)
  Float_waitrecv = float(txt_waitrecv)
  
  data =''
  print('\r\nServer',txt_ip ,':', str(Int_port) )
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(Float_waitrecv) #wait timeout 300ms
  
  try:
    s.connect((txt_ip, Int_port))
    binary_data = binascii.unhexlify(message)
    print('Check Input HEX: ' + str(binascii.hexlify(binary_data)).upper())
    s.sendall(binary_data)
    #s.settimeout(Float_waitrecv) #wait timeout 300ms
    data = s.recv(1024)
    
  except OSError:
    print('\r\ns.err')
  
  finally:
    s.close()
  
  if len(data)>0 :
    print( 'Received : ', data + ' len = ' + str(len(data)))
    #if (sys.platform.upper() != 'WIN32') and (sys.platform.upper() != 'LINUX'):
    #  print( 'Received : ', data + ' len = ' + str(len(data)))
    #else:
    #  print( 'Received : ', str(data) + ' len = ' + str(len(data))) ##fix cross WIN32

    # #print(str(data))
    data = str(binascii.hexlify(data)).upper()
    # #print(data)
    data = data.replace('B\'', '')
    data = data.replace('b\'', '')
    data = data.replace('\'', '')
    
    #print(data)
    print( 'Received HEX: ', data + ' len = ' + str(len(data)) +  ' len/2 = ' + str(len(data)/2))
    #data = json.dumps({'tag': '11/00','data': data})
    #print( 'Received JSON: ', data)
  #print(data)
  return data
  
def RTU_poll(jmessage):
  # return '' if false
  # return data if process ok
  my_intype = ''
  my_message = ''
  my_txt_ip = ''
  my_txt_port = ''
  my_txt_waitrecv = ''
  
  print('RTU_poll running')
  print(jmessage)  
  try:
    json_object = json.loads(jmessage)
  except ValueError as e:
    print('JSON input err')
    return ''
  print(json_object)
  
  try:
    my_intype = json_object["type"]
    my_message = json_object["data"]
    my_txt_ip = json_object["ipd"]
    my_txt_port = json_object["portd"]
    my_txt_waitrecv = json_object["waitresp"]
   
    #debug
    print(my_intype,my_message,my_txt_ip,my_txt_port,my_txt_waitrecv)

  except KeyError as e:
    print('JSON Get Key 1 err')
    return ''  
  
  if my_intype == 'raw_hex':
    #ifsendhex_and_closed("3132330D0A","192.168.10.150","5021","2")
    data = ifsendhex_and_closed(my_message,my_txt_ip,my_txt_port,my_txt_waitrecv)
  else:
    print('Incorrect type of operation')
    return ''  
  
  json_object["ticks_ms"] = str(time.ticks_ms()) #ticks_ms
  json_object["ifconfig_ip"] = str(wlan.ifconfig()[0])

  #if (sys.platform.upper() != 'WIN32') and (sys.platform.upper() != 'LINUX'):
  #  json_object["ticks_ms"] = str(time.ticks_ms()) #ticks_ms
  #  json_object["ifconfig_ip"] = str(wlan.ifconfig()[0])
  #else:
  #  json_object["ticks_ms"] = str(int(time.time_ns()/1000)) #time_ns/1000 to ticks_ms ##fix cross WIN32
  #  json_object["ifconfig_ip"] = str(socket.gethostbyname(socket.gethostname())) ##fix cross WIN32

  if len(data) >=2:
    json_object["type"] = json_object["type"] + "__resp" # mod type resp
    json_object["data_resp"] = data #add data_resp
    #json_object["ticks_ms"] = str(time.ticks_ms()) #ticks_ms
    #json_object["ifconfig_ip"] = str(wlan.ifconfig()[0])
  else:
    json_object["type"] = json_object["type"] + "__TimeoutError" # mod type resp

  data = json.dumps(json_object)
  print(data)
  return data  
  
  
  
print('Test protcol')
#ifsendhex_and_closed(message,L_ip,L_port,L_waitrecv):
#ifsendhex_and_closed("3132330D0A","192.168.10.150","5021","2")

#time.sleep(1)  
#istring ='''{"data": "4142433132330D0A", "tag": "11/00"}
#'''
#RTU_poll(istring)
#RTU_poll("$$$")
#tstring = '''{"tag": "11/00", "type": "raw_hex", "data": "3132330D0A","ipd": "192.168.10.150","portd": "5021", "waitresp": "1.9"}
#'''
#RTU_poll(tstring)
#time.sleep(20)
#RTU_poll(tstring)


print('main2-esp32' + VERSION_MAINPROG)
print('Wait 5s to enter program')
time.sleep(5)
wdt_feed()
#proc_helloPubSub()
c = MQTTClient(CLIENT_ID, MQTT_SERVER, keepalive=MQTT_ALIVE)
# Print diagnostic messages when retries/reconnects happens
c.DEBUG = True
c.set_callback(sub_cb)

time.sleep(3)

if not c.connect(clean_session=True): #Refresh clean_session=True or don't change clean_session=False
  print('New session being set up')
  print(MQTT_SERVER)
  print(MQTT_SUBTOPIC1)
  c.subscribe(MQTT_SUBTOPIC1)
  
  if MQTT_PUBSUBBROADCAST_TOPIC0 !='':
    print('Dbg: bc')
    print(MQTT_PUBSUBBROADCAST_TOPIC0)
    c.subscribe(MQTT_PUBSUBBROADCAST_TOPIC0) #add Multiple topic
    time.sleep(0.5)
  

time.sleep(0.5)
proc_helloPub()

micropython.mem_info()
micropython.qstr_info()

while True:
  led.value(LED_ASSERT) #Set led turn on
  time.sleep(0.1)
  led.value(LED_DEASSERT) #Set led turn off
  time.sleep(0.2)
  c.wait_msg()
  print(str(wlan.ifconfig()))

#end of operation
c.disconnect()
time.sleep(20)  
machine.reset()

