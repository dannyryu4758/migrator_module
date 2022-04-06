#!/bin/sh

IMAGE_TAG=migrate_module
SERVICE_NAME=migrate_module

echo "building ${IMAGE_TAG} ..."
docker build -t ${IMAGE_TAG} .

echo "drop container ${SERVICE_NAME}"
docker rm -f ${SERVICE_NAME}

echo "run service from ${IMAGE_TAG}"
docker run -it  \
    --name ${SERVICE_NAME} \
    ${IMAGE_TAG}

docker container ls
