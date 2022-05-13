
  
FROM python:3.9.7
ENV PYTHONUNBUFFERED 1

#RUN apk add build-base
WORKDIR /server
COPY . /server/

RUN pip3 install --upgrade pip
RUN pip3 install wheel
RUN pip3 install -r requirements.txt

RUN chmod +x entrypoint.sh
RUN chmod +x entrypoint-client.sh
# RUN chmod +x entrypoint-aux.sh