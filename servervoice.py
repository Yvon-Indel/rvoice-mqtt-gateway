#!/usr/bin/python3
# -*- coding: utf-8 -*-
#@Yvon_Indel - 05/2020
#V1.0
#https://github.com/Yvon-Indel
#The purpose of this script is to use Responsive Voice TTS (https://responsivevoice.org/) with Home Assistant.
# Thanks to @HelloChatterbox - https://github.com/HelloChatterbox/py_responsivevoice for the Unofficial python API for Responsive Voice
#
# How it work:
# 1- Script wait for a MQTT message text , 
# 2- Script send the message to Responsive Voice services and download the TTS mp3 file to \tmp
# 3- Script send a MQTT message with the url to the mp3 file for playback
# The web server is serving on port 8000 by default

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import posixpath
import argparse
import urllib
import os
import sys
from responsive_voice import ResponsiveVoice
import socketserver
import http.server
import multiprocessing
#Env variable : should be set in config.ini and send in docker run command 
LISTEN_TOPIC=os.getenv("LISTEN_TOPIC","/tts/message")
STATUS_TOPIC=os.getenv("STATUS_TOPIC","/tts/connect")
PUBLISH_TOPIC=os.getenv("PUBLISH_TOPIC","/tts/lienmp3")
MQTT_ADRESS=os.getenv("MQTT_ADRESS")
MQTT_PORT=int(os.getenv("MQTT_PORT","1883"))
MQTT_LOGIN=os.getenv("MQTT_LOGIN")
MQTT_PASS=os.getenv("MQTT_PASS")
HTTP_PORT=int(os.getenv("HTTP_PORT","8000"))
HTTP_IP=os.getenv("HTTP_IP")
TTS_LANG=os.getenv("TTS_LANG","ResponsiveVoice.FRENCH")
TTS_GENDER=os.getenv("TTS_GENDER","ResponsiveVoice.MALE")
engine = ResponsiveVoice(lang=ResponsiveVoice.FRENCH,gender=ResponsiveVoice.MALE)
if MQTT_ADRESS is None:
    sys.exit("Error: please set Ip adress of the MQTT brocker: MQTT_ADRESS=xx.xx.xx.xx")
    
if MQTT_LOGIN is None:
    sys.exit("Error: please set login of the MQTT brocker : MQTT_LOGIN=your_login")

if MQTT_PASS is None:
    sys.exit("Error: please set password of the MQTT brocker: MQTT_PASS=your_password")

if HTTP_IP is None:
    sys.exit("Error: please set the IP of this server : HTTP_IP=Ip_of_the_server")     

def serveur_http():
  # Variables
    os.chdir("/tmp/")
    # Setup simple sever
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", HTTP_PORT), Handler) as httpd:
        print("serving at port", HTTP_PORT)
        # start the server as a separate process
        server_process = multiprocessing.Process(target=httpd.serve_forever)
        server_process.daemon = True
        server_process.start()

def lienmp3(message):
  file_path = engine.get_mp3(message)
  return file_path;


def on_connect(client, userdata, flags, rc):
  print("Connecté to MQTT broker")
  ret=client.publish(STATUS_TOPIC,"Online",0,True)
  
def on_disconnect(client, userdata, flags, rc):
  print("Connecté to MQTT broker")
  ret=client.publish(STATUS_TOPIC,"Offline",0,True)
  
def on_message(client, userdata, msg):
    
    try:
        message= msg.payload.decode('utf-8')
    except UnicodeEncodeError:
        message= msg.payload    
    print("Message détecté :",message)
    lien=lienmp3(message)
    lien= lien.replace("tmp/","")
    lien="http://" + HTTP_IP + ":" + str(HTTP_PORT) + lien
    print(lien)
    ret=client.publish(PUBLISH_TOPIC,lien)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Souscription au topic : " + str(mid) +" with QoS " + str(granted_qos))


def on_publish(client,userdata,result):
    print("Lien publié \n")
    pass
def on_log(client, userdata,level,buf):
    print("log: ",buf)

def partiemqtt():

  qos=1

  client = mqtt.Client()

  client.username_pw_set( MQTT_LOGIN , MQTT_PASS )
  
  client.on_log=on_log  
 
  client.connect( MQTT_ADRESS, int(MQTT_PORT), 60)

  client.subscribe( LISTEN_TOPIC , qos=1)

  client.on_connect = on_connect
  
  client.on_disconnect = on_disconnect

  client.on_subscribe = on_subscribe ("","",LISTEN_TOPIC , qos)

  client.on_message = on_message

  client.on_publish = on_publish

  client.loop_forever()

running = True


while running:
    try:
        serveur_http()
        partiemqtt()
    except (KeyboardInterrupt, SystemExit):
        running = False
        print("Finish current jobs and shut down. If you need force exit use kill")
        publish.single(STATUS_TOPIC,"Offline", qos=0, retain=True, hostname=MQTT_ADRESS, port=MQTT_PORT, auth= {'username':MQTT_LOGIN, 'password':MQTT_PASS})
        
    except Exception as e:
        print("Fatal error while executing worker command: %s", type(e).__name__)
        publish.single(STATUS_TOPIC,"Offline", qos=0, retain=True, hostname=MQTT_ADRESS, port=MQTT_PORT, auth= {'username':MQTT_LOGIN, 'password':MQTT_PASS})
        raise e