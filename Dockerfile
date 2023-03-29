FROM python:3.8-slim-buster

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt
COPY . /app

#ARG cert_folder
#RUN mkdir cert
#COPY  $cert_folder ./cert
#COPY /Users/dangchu/Documents/GitRepo/secret/cert/. ./cert

#ENTRYPOINT ["python","./app/test.py"]
ENTRYPOINT ["python","./app/get_tweet.py"]