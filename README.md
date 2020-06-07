Work still in progress...

# rvoice-mqtt-gateway

A  Python script which provides a [Responsive Voice](https://responsivevoice.org/) TTS to MQTT gateway for my own use with [Home Assistant](https://www.home-assistant.io/docs/)

## Features

* Listen for TTS request from MQTT
* Query mp3 from Responsive Voice server
* Data publication of the TTS mp3 link on MQTT
* Web Server for local mp3 playback
* MQTT authentication support
* Run in Docker

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

#### Install Docker and a MQTT brocker

You need to have [Docker](https://docs.docker.com/get-docker/) and a [Mqtt brocker](https://mosquitto.org/) installed.

Installations procedures are not developped here.

#### Create a free account on [Responsive Voice](https://responsivevoice.org/)

You need to create a free account on the website in order to get your own server key.

After login, find the panel "your site code", the key is on the right : "key=XXXXXXX" 


## Configuration

Create the file "config.ini" and add informations inside according to your own need:

* LISTEN_TOPIC is the mqtt topic to send the message you want to TTS
* STATUS_TOPIC is the mqtt topic of the stae of the gateway ("Online","Offline")
* PUBLISH_TOPIC is the topic published with the mp3 link of the TTS file
* MQTT_ADRESS is the IP adress of the mqtt brocker
* MQTT_PORT is the port number of the mqtt brocker (default=1883)
* MQTT_LOGIN is the login of the mqtt brocker
* MQTT_PASS is the of password the mqtt brocker
* HTTP_IP is the ip adress of the local web server (Docker host) used for link playback (ex: http://192.168.1.62:8000/3069301452616694024.mp3)
* HTTP_PORT is the port of the local web server
* TTS_LANG is the language of the TTS (not used yet)
* TTS_GENDER is the gender of the TTS language (not used yet)
* RVOICE_KEY=XXXXXXXX is your Responsive Voice server Key.


example:
```sh
LISTEN_TOPIC=/tts/message
STATUS_TOPIC=/tts/connect
PUBLISH_TOPIC=/tts/lienmp3
MQTT_ADRESS=192.168.1.27
MQTT_PORT=1883
MQTT_LOGIN=loginmqtt
MQTT_PASS=123456
HTTP_IP=192.168.1.62
HTTP_PORT=8000
TTS_LANG=ResponsiveVoice.FRENCH
TTS_GENDER=ResponsiveVoice.MALE
RVOICE_KEY=XXXXXXXX
```
## How it work

* Send a mqtt message on the LISTEN_TOPIC with the message you want to tts as payload.
* You get back a mqtt message on the PUBLISH_TOPIC with the local url of the tts mp3 file as payload.

If you send: 
```shell
topic : /tts/message
payload: Attention, la porte est ouvert.
```
you get:
```shell
topic : /tts/lienmp3
payload: http://192.168.1.62:8000/-7524597403686428361.mp3
```

You just have to pass the url link to your home automation system for playback on your sound device.

## Deployment

### Docker

if the server port is 8000 in your config.ini file, run the command below or adapt the port number in the command line to your need:

```shell
sudo docker run --env-file config.ini -p 8000:8000 --restart=unless-stopped --name RVoiceServer yvonindel/rvoiceserver:v1.0
```
   
## To do list
Only FRENCH language is working now. Don't know why.
Sometime the gender is not working. Seems to be an Responsive Voice issue.

## Authors

It's my own code, based on the work of this github repo:

* [HelloChatterbox](https://github.com/HelloChatterbox/py_responsivevoice)

## License

[GPL3-0](https://github.com/Yvon-Indel/rvoice-mqtt-gateway/blob/master/LICENCE)
