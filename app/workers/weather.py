from multiprocessing import Process, Manager, Queue
import time
import urllib2
import json
import pickle
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class get_temp():
    def __init__(self, *args, **kwargs):
        weather = {'curr_temp': 0}
        while True:
            try:
                logger.warning('Fetching weather.')
                f = urllib2.urlopen('http://api.wunderground.com/api/38c037db62bd609c/geolookup/conditions/q/AZ/Goodyear.json')
                json_string = f.read()
                parsed_json = json.loads(json_string)
                location = parsed_json['location']['city']
                temp = str(parsed_json['current_observation']['temp_f'])
                weather["curr_temp"] = temp
                pickle.dump(weather, open('weather.pickle','wb'))
                logger.info('Temp Update: %s', weather['curr_temp'])
                time.sleep(900)
            except Exception as err:
                logger.error('Weather Error: %s', err)
