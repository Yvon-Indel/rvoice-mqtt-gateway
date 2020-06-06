FROM python:slim-buster
ADD servervoice.py /
RUN pip3 install paho-mqtt
RUN pip3 install ResponsiveVoice
CMD [ "python3", "./servervoice.py" ]
 
