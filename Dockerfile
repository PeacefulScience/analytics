FROM ubuntu:latest

COPY requirements.txt /tmp/
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev 

RUN pip install --requirement /tmp/requirements.txt
