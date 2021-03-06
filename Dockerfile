FROM ubuntu:latest

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
