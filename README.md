## Blinky LED

* Usage:
```
$ pip install --editable .
$ blinky --help
```

* DOCKER

```
$ docker build -t blinky-led https://github.com/azcoigreach/blinky-led.git
$ docker run -tdi -c 0 --privileged --restart unless-stopped --name blinky-led blinky-led
```