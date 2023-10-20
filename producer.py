#!/usr/bin/env python
""" A producer of CDEK's webhooks
"""

import json
import time
import random
import uuid
import requests

from faker.providers import BaseProvider
from faker import Faker

import producer_config as config

class TaskProvider(BaseProvider):
    """ Define a TaskProvider
    """
    # pylint: disable=no-self-use
    def event_type(self):
        """ event_type
        """
        types = [
            'ORDER_STATUS'
            # 'ORDER_STATUS', 'PRINT_FORM', 'DOWNLOAD_PHOTO', 'PREALERT_CLOSED'
        ]
        return types[random.randint(0, len(types)-1)]


# Create a Faker instance and seeding to have the same results every time we execute the script
# Return data in English
fakeTasks = Faker('en_US')
# Seed the Faker instance to have the same results every time we run the program
fakeTasks.seed_instance(0)
# Assign the TaskProvider to the Faker instance
fakeTasks.add_provider(TaskProvider)

def get_attributes(arg_type):
    """ Attrs composition
    """
    if arg_type == 'ORDER_STATUS':
        attrs = {
                "is_return": False,
                "cdek_number": 1111111111,
                "number": 41276666,
                "status_code": 11,
                "status_date_time": fakeTasks.date_time_this_year(),
                "city_name": "Санкт-Петербург",
                "code": 11,
                "is_reverse": False,
                "is_client_return": False
                }
    elif arg_type == 'PRINT_FORM':
        attrs = {
                "type": "barcode",
                "url": "https://api.cdek.ru"
                }
    elif arg_type == 'DOWNLOAD_PHOTO':
        attrs = {
                "cdek_number": 1111111111,
                "link": "https://api.cdek.ru"
                }
    elif arg_type == 'PREALERT_CLOSED':
        attrs = {
                "prealert_number": 2222222222,
                "close_date": fakeTasks.date_time_this_year(),
                "fact_shipment_point": "SPB9"
                }
    return attrs


def produce_task():
    """ Message composition
    """
    loc_ev_type = fakeTasks.event_type()
    message = {
        #'type': fakeTasks.event_type()
        'type': loc_ev_type
        ,'date_time':fakeTasks.date_time_this_year()
        ,'uuid': str(uuid.uuid4())
        ,'attributes': get_attributes(loc_ev_type)
    }
    return message


def send_webhook(arg_msg):
    """
    Send a webhook to a specified URL
    :param msg: task details
    :return:
    """
    try:
        # Post a webhook message
        # default is a function applied to objects that are not serializable =
        # it converts them to str
        loc_resp = requests.post(config.WEBHOOK_RECEIVER_URL, data=json.dumps(
            arg_msg, sort_keys=True, default=str), headers={'Content-Type': 'application/json'},
            timeout=1.0)
        # Returns an HTTPError if an error has occurred during the process (used for debugging).
        loc_resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("An HTTP Error occurred",repr(err))
        #pass
    except requests.exceptions.ConnectionError as err:
        print("An Error Connecting to the API occurred", repr(err))
        #pass
    except requests.exceptions.Timeout as err:
        print("A Timeout Error occurred", repr(err))
        #pass
    except requests.exceptions.RequestException as err:
        print("An Unknown Error occurred", repr(err))
        #pass
    #except:
    #    pass
    #else:
    return loc_resp.status_code

# Generate A Bunch Of Fake Tasks
def produce_bunch_tasks():
    """
    Generate a Bunch of Fake Tasks
    """
    num = random.randint(config.MIN_NBR_TASKS, config.MAX_NBR_TASKS)
    num = 2
    for i in range(num):
        loc_msg = produce_task()
        loc_resp = send_webhook(loc_msg)
        time.sleep(config.WAIT_TIME)
        print(i, "out of ", num, " -- Status", loc_resp, " -- Message = ", loc_msg)
        yield loc_resp, num, loc_msg


if __name__ == "__main__":
    for resp, total, msg in produce_bunch_tasks():
        pass
