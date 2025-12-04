FROM ubuntu:jammy-20240911.1

WORKDIR /sandbox

COPY ./dockerfiles/requirements.txt .

RUN apt-get update
RUN apt-get install gdal-bin -y
RUN apt-get install libgdal-dev -y
RUN apt-get install python3-pip -y
RUN apt-get install python3-setuptools -y

RUN pip3 install -r requirements.txt
RUN rm requirements.txt

EXPOSE 8000

ENTRYPOINT ["tail", "-f", "/dev/null"]