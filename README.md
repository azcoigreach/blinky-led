## Blinky LED

* RUN
```
python app/led_master.py
```

* DOCKER

```
$ git clone https://github.com/azcoigreach/blinky-led.git
$ cd blinky-led
$ docker build -t blinky-led .
$ docker run -tdi --privileged --restart unless-stopped blinky-led
```