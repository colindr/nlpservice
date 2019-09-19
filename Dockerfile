FROM python:3

RUN mkdir /code
WORKDIR /code

# install tweetnlp requirements
COPY lib/requirements.txt /code/lib/requirements.txt
RUN pip install -r /code/lib/requirements.txt

# install tweetnlp
COPY lib/tweetnlp /code/lib/tweetnlp
COPY lib/setup.py /code/lib/setup.py
RUN pip install ./lib

# copy django deps
COPY django/requirements.txt /code/django/requirements.txt

RUN pip install -r django/requirements.txt

COPY django /code/django

RUN mkdir /data
COPY creds.json /creds.json
ENV NLPSERVICE_TWITTER_CREDS_FILE  /creds.json

WORKDIR /code/django
