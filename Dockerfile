FROM arm32v7/python:2.7.14-jessie

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y python-pil && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY /app ./

CMD ["python", "led_master.py"]