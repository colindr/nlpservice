FROM python:3

RUN mkdir /code
WORKDIR /code

# install tweetnlp requirements
COPY lib/requirements.txt /code/lib/requirements.txt
RUN pip install -r /code/lib/requirements.txt

# install tweetnlp
COPY lib /code/lib
RUN pip install ./lib

# copy django deps
COPY django/requirements.txt /code/django/requirements.txt

RUN pip install -r django/requirements.txt

COPY django /code/django

RUN mkdir /data
COPY creds.yml /creds.yml
ENV NLPSERVICE_TWITTER_CREDS_FILE  /creds.yml

WORKDIR /code/django
