from multiprocessing import Process, Manager
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class weather(d):
    def __init__(self, *args, **kwargs):
        global d
        while True:
            logger.warning('Fetching weather.')
            f = urllib2.urlopen('http://api.wunderground.com/api/38c037db62bd609c/geolookup/conditions/q/AZ/Goodyear.json')
            json_string = f.read()
            parsed_json = json.loads(json_string)
            location = parsed_json['location']['city']
            t = parsed_json['current_observation']['temp_f']
            self.temp = t
            d['curr_temp'] = self.temp
            logger.info('Temp Update: %s', d['curr_temp'])
            time.sleep(900)

