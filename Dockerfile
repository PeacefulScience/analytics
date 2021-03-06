FROM ubuntu:latest

COPY requirements.txt /tmp/
RUN pip3 install --requirement /tmp/requirements.txt
