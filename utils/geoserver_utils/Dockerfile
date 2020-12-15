FROM python:3.7-slim

#RUN apk --update add git wget vim
RUN apt-get update && apt-get -y install vim && \
  apt-get -y install wget && apt-get -y install nano 
RUN mkdir opt/geoserver && mkdir opt/geoserver/data_dir
 
#RUN mkdir /tmp/geoserver_utils
WORKDIR /tmp
COPY *.* /tmp/
#COPY index.html /usr/share/nginx/html/doc/api/.
#COPY api.conf /etc/nginx/conf.d/default.conf

RUN python -m pip install --upgrade pip && \
  pip install -r requirements.txt --no-cache-dir
