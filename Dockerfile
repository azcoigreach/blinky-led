FROM arm32v7/python:2.7.14-jessie

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
			libffi-dev libxml2-dev libxslt1-dev \
			libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev \
			liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install Pillow

RUN mkdir /usr/data

COPY /app ./

ADD entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/bin/sh", "-c", "./entrypoint.sh"]