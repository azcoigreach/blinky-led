FROM arm32v7/python:2.7.14-jessie

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y libffi-dev libxml2-dev libxslt1-dev \
        libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev \
        liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY /app ./

CMD ["python", "led_master.py"]