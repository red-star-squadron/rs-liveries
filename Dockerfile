FROM ubuntu:22.04
RUN apt update -y
RUN apt install python3.10 wget -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.10 get-pip.py
RUN python3.10 -m pip install pipenv
WORKDIR /work
