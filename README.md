## Blinky LED

* RUN
```
python app/led_master.py
```

* DOCKER

```
$ docker build -t blinky-led https://github.com/azcoigreach/blinky-led.git
$ docker run -tdi -c 0 --privileged --restart unless-stopped --name blinky-led blinky-led
```