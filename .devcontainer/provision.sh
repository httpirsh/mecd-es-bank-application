#!/bin/bash

apt update -y

apt install awscli -y

pip install -r .devcontainer/requirements.txt

