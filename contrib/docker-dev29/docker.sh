#!/bin/bash

docker build -t ckan29 -f Dockerfile .

if [ "$1" == "run" ] ; then
    docker run --name ckan29 -d -p 80:80 -p 3122:22 -p 5432:5432 ckan29
fi
