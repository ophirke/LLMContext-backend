#!/usr/bin/env bash

CONTAINER_NAME="iris-comm"
PORT1="1972:1972"
PORT2="52773:52773"
IRIS_PASSWORD="demo"
IRIS_USERNAME="demo"
IMAGE="intersystemsdc/iris-community:latest"

docker remove $CONTAINER_NAME

docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT1 \
    -p $PORT2 \
    -e IRIS_PASSWORD=$IRIS_PASSWORD \
    -e IRIS_USERNAME=$IRIS_USERNAME \
    $IMAGE