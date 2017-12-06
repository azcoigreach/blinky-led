FROM arm32v7/python:2.7.14-jessie

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /usr/data

COPY /app ./

ADD entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/bin/sh", "-c", "./entrypoint.sh"]