FROM docker.elastic.co/logstash/logstash:7.3.2
RUN rm -f /usr/share/logstash/pipeline/logstash.conf
ADD pipeline/ /usr/share/logstash/pipeline/
ADD config/ /usr/share/logstash/config/
RUN mkdir /usr/share/logstash/templates
ADD tweets.json /usr/share/logstash/templates/tweets.json
