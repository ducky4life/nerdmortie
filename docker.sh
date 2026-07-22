#!/bin/bash

git pull
docker stop nerdmortie
docker build -t nerdmortie:latest -f Dockerfile .
docker run --rm --name nerdmortie nerdmortie:latest
