class weather():
    def __init__(self, *args, **kwargs):
        while True:
            logger.warning('Fetching weather.')
            f = urllib2.urlopen('http://api.wunderground.com/api/38c037db62bd609c/geolookup/conditions/q/AZ/Goodyear.json')
            json_string = f.read()
            parsed_json = json.loads(json_string)
            location = parsed_json['location']['city']
            t = parsed_json['current_observation']['temp_f']
            self.temp = t
            curr_temp.value = self.temp
            logger.info('Temp Update: %s', curr_temp.value)
            time.sleep(900)

