#!/bin/bash

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 831731636870.dkr.ecr.us-east-1.amazonaws.com
docker build -t outbound-producer .
docker tag outbound-producer:latest 831731636870.dkr.ecr.us-east-1.amazonaws.com/outbound-producer:latest
docker push 831731636870.dkr.ecr.us-east-1.amazonaws.com/outbound-producer:latest

