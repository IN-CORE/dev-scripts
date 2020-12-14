FROM python:alpine

RUN apt-get -qq update && apt-get -qq install git

#RUN mkdir /tmp/geoserver_utils
WORKDIR /tmp
COPY geoserver_utils .
COPY index.html /usr/share/nginx/html/doc/api/.
COPY api.conf /etc/nginx/conf.d/default.conf

RUN pip install -r requirements.txt --no-cache-dir
