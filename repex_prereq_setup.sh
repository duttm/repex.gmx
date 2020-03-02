#!/bin/bash

sudo docker rm $(sudo docker ps -aq)
sudo docker run -d --name rmq_1 -P rabbitmq:3
sudo docker ps
export RADICAL_PILOT_DBURL=mongodb://repex_3:r3p3x_3@two.radical-project.org:27017/repex_3
export RMQ_PORT=32769
echo $RADICAL_PILOT_DBURL
echo $RMQ_PORT