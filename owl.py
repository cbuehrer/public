#!/usr/bin/python3

# Still have no clue why this works but somehow it does ¯\_(ツ)_/¯
# It will query data from the electic owl (cm160) via USB
# and sent it to an MQTT broker. I consume the data with homeassisstant in the end

import serial
from time import sleep, time

##
# config

cm160dev = "/dev/ttyUSB_OWL"
interval = 5
mqtt_broker = "localhost"
mqtt_port = 1883

#
##

##
# MQTT shit
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt with result code " + str(rc))

def send_data(s):
    amps = ((s[9] << 8) | s[8])
    watts = round(amps * 0.7 * 230 / 10, 2)
    #print("Watts: " + str(watts) + " Amps: " + str(amps))
    client.publish("homeassistant/home/powerconsumption", watts)

client = mqtt.Client()
client.on_connect = on_connect
client.connect(mqtt_broker, mqtt_port, 60)
client.loop_start()

ser = serial.Serial(cm160dev, 250000, timeout=1)

while True:
    sleep(interval)
    s = ser.read(11) # read up to ten bytes (timeout)
    if s == b'\xa9IDTCMV001\x01':
        #print(s)
        ser.write(b'Z')
        s = ser.read(11)
    if len(s) == 0:
        #print("empty")
        continue

    if int(s[0]) == 81:
        send_data(s)
    elif int(s[0]) == 89:
        send_data(s)
    elif "WAIT" in str(s):
        #print("We shall wait")
        ser.write(b'\xA5')
        s = ser.read(11)
    elif s == b'\xa9IDTCMV001\x01':
        #print(str(s))
        ser.write(b'Z')
#    else:
        #dont give a shit
        #print("What ever: " + str(s))

