#!/bin/bash

docker build --no-cache -t "antoniolauro/webapp:latest" .

docker push "antoniolauro/webapp:latest"

kubectl delete deploy/django --ignore-not-found=true

kubectl apply -f "manifests/"