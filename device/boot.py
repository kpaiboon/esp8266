# This file is executed on every boot (including wake-boot from deepsleep)

import esp
#esp.osdebug(None)
import os
import uos
import machine
import gc
import micropython
import sys
import time
import network
import ubinascii as binascii

VERSION_MAINPROG = 'V0.10--2019--init_code'

networks = (
    ('TCC11', 'CCBBAA332211', '', '','', ''),
    ('EW200', '0618055704', '', '','', ''),
    #('SSID4', 'somepass', '192.168.7.89', '255.255.255.0', '192.168.7.1', '8.8.8.8'),
    #('NETGEARHome25', 'whateverpasswd', '192.168.1.89', '255.255.255.0','192.168.1.1', '8.8.8.8'),
    #('myotherwifinet', 'somepass', '192.168.2.89', '255.255.255.0', '192.168.2.1', '8.8.8.8'),
    #('SSID3', 'whateverpasswd', '192.168.4.89', '255.255.255.0','192.168.4.1', '8.8.8.8'),
    #('SSID4', 'somepass', '192.168.7.89', '255.255.255.0', '192.168.7.1', '8.8.8.8'),
)



changeCPUspeed = True
if changeCPUspeed:
    machine.freq(80000000) # set the CPU frequency to 80 MHz
print('CPU : ' + str(machine.freq()))

#uos.dupterm(None, 1) # disable REPL on UART(0)


micropython.alloc_emergency_exception_buf(100)
micropython.mem_info('verbose')
micropython.qstr_info('verbose')
micropython.mem_info()
micropython.qstr_info()

#import webrepl
#webrepl.start()

gc.collect()
gc.enable()


i = 30
while i>0:
    i = i -1
    time.sleep(0.2)
    print('.' + str(i))
  
print('..boot..')
def drive_info():
    print(os.uname()) 
    print(os.getcwd())
    print(os.listdir())  
    fs_stat = os.statvfs('/')
    fs_size = fs_stat[0] * fs_stat[2]
    fs_free = fs_stat[0] * fs_stat[3]
    print('File Sys sz {:,} - Free {:,}'.format(fs_size, fs_free))
  
drive_info()

string_esp32 = 'ESP32'
string_esp8266 = 'ESP8266'
if(sys.platform.upper() =='ESP32' ):
    mystring = string_esp32
else:
    mystring = string_esp8266
  
print(mystring)        
print(binascii.hexlify(network.WLAN().config('mac'),':').decode().upper())

## Simple software WDT implementation
print('\n\r\nwatchdog_init') 
time.sleep(1)
wdt_onedayrebootminute = 59 # 0 or one day reboot in 55 minute
wdt_upperlimitminute = 10 # 0 or watchdog reboot in 10 minute
wdt_wlanreconn = 5 # 0 or wlan watchdog reboot in 5 minute


wdt_counter_oneday = 0
wdt_counter = 0
wdt_wlancounter = 0
wdt_counter_autosoftreboot = 0 # 0 or soft reboot 3 minute
def wdt_callback():
  global wdt_counter_oneday
  global wdt_counter
  global wdt_wlancounter
  global wdt_counter_autosoftreboot
  wdt_counter_oneday += 1
  wdt_counter += 1
  wdt_wlancounter += 1

  
  if (wdt_counter_oneday >= wdt_onedayrebootminute) and  ( wdt_onedayrebootminute !=0):
    print('\n\r\n !!wdt..r..one-day..')
    machine.reset()
    
  if (wdt_counter >= wdt_upperlimitminute) and  ( wdt_upperlimitminute !=0):
    print('\n\r\n !!wdt..r..now')
    machine.reset()
    
  if (wdt_counter >= (wdt_upperlimitminute*0.5)) and  ( wdt_upperlimitminute !=0):
    print('\n\r\n !!wdt..> 50%')
    
  if (wdt_wlancounter >= wdt_wlanreconn) and  ( wdt_wlanreconn !=0):
    wdt_wlancounter = 0
    if wlan.isconnected():
      print('wdt_wlan_Connected OK')
    else:
      print('!!wdt No internet, R> in 5s')
      time.sleep(5)
      machine.reset()
  
  if (wdt_counter_autosoftreboot !=0):  
    if(wdt_counter_autosoftreboot >0):
      wdt_counter_autosoftreboot = wdt_counter_autosoftreboot -1
    print('\n\r\n !!auto..r..act\r\n >: ' + str(wdt_counter_autosoftreboot))
    if (wdt_counter_autosoftreboot <= 1):
      print('\n\r\n !!auto..r..now\r\n')
      machine.reset()

def wdt_feed():
  global wdt_counter
  wdt_counter = 0
  print('Dbg: call wdt_f()')

def wdt_autoreboot(n):
  global wdt_counter_autosoftreboot
  print('Dbg: call wdt_ar()')
  if(n>=1):
    wdt_counter_autosoftreboot = n+1
    print('(n+1) : ' + str(wdt_counter_autosoftreboot))
  else:
    wdt_counter_autosoftreboot = 0
    print('Dis: wdt_counter_autosoftreboot = 0')
    
#wdt_timer = machine.Timer(-1)
wdt_timer = machine.Timer(555)
wdt_timer.init(period=60000, mode=machine.Timer.PERIODIC, callback=lambda t:wdt_callback()) #timer resolution 60sec
## END Simple software WDT implementation



wlan = network.WLAN(network.STA_IF)
wlan.active(False)         # deactivate the interface
ap = network.WLAN(network.AP_IF) # create access-point interface
ap.active(False)         # deactivate the interface
  
wlan.active(True)
time.sleep(2)


print('Scan WiFi: (ssid, bssid, channel, RSSI, authmode, hidden)')
time.sleep(5) # this ensures a full network scan
scan_r = wlan.scan()
for net in scan_r:
  print(net)

cnt = 0
iswlanready = False
while (cnt < len(networks)) and (not iswlanready):
  WL_SSID = networks[cnt][0]
  WL_PASSWD = networks[cnt][1] 
  print('S>SSID: ' + WL_SSID + ' C: ' + str(cnt) )
  wlan.connect(WL_SSID,WL_PASSWD)
  if networks[cnt][2] != '':
    print('Fixed IP:')
    WL_IPADDRESS = networks[cnt][2]
    WL_NETMASK = networks[cnt][3]
    WL_GATEWAY = networks[cnt][4]
    WL_DNS = networks[cnt][5]
    print('S>IPADDR: ' + WL_IPADDRESS)
    print('S>NETMASK: ' + WL_NETMASK)
    print('S>GATEWAY: ' + WL_GATEWAY)
    print('S>DNS: ' + WL_DNS)
    wlan.ifconfig(WL_IPADDRESS, WL_NETMASK, WL_GATEWAY, WL_DNS) #depends firmware
  
  start = time.ticks_ms()
  time.sleep(5) # this ensures a full connect
  to = 50000 # 30 x [1000 ms]
  while (not wlan.isconnected()) and time.ticks_diff(time.ticks_ms(), start) < to:
    print('wlan Act: ' + str(wlan.active()) + ' code: ' + str(wlan.status())  )
    print('DIFF#ms ' + str(time.ticks_diff(time.ticks_ms(), start)) + ' #to ' + str(to))
    time.sleep_ms(2000) #wait get wlan status
    
  if wlan.isconnected():
    print('Connected')
    iswlanready = True
  else:
    print('Try next list')
    cnt = cnt +1
    time.sleep(1)
  
if wlan.isconnected():
  print('wlan conn succeeded: ' +str(wlan.isconnected()))
  print('wlan IP: ' +str(wlan.ifconfig()))
else:
  print('No internet, R> in 5s')
  time.sleep(5)
  machine.reset()

micropython.mem_info()
micropython.qstr_info()

print('Next App..')

i = 5
while i>0:
  i = i -1
  time.sleep(1)
  print('.' + str(i))


