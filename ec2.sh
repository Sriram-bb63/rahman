#!/bin/bash
apt update && apt install -y docker.io git
git clone https://github.com/Sriram-bb63/rahman.git
cd rahman
docker build -t flask-app .
docker run -d -p 80:5000 flask-app
