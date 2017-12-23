from multiprocessing import Process, Manager, Queue
import time
import urllib2
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def weather():
    
    while True:
        
        logger.warning('Fetching weather.')
        f = urllib2.urlopen('http://api.wunderground.com/api/38c037db62bd609c/geolookup/conditions/q/AZ/Goodyear.json')
        json_string = f.read()
        parsed_json = json.loads(json_string)
        location = parsed_json['location']['city']
        temp = parsed_json['current_observation']['temp_f']
        d["curr_temp"] = temp
        logger.info('Temp Update: %s', d['curr_temp'])
        time.sleep(15)

