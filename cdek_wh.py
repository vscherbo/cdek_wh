#!/usr/bin/env python
""" CDEK webhooks listener
gunicorn -w 2 -b 0.0.0.0:3000 myapp:app
"""

import sys
import logging
import json

from flask import Flask, request, Response
import psycopg2

#from pg_app import PGapp
#import log_app
import cdek_wh_config

INSERT_CDEK_STATUS = u"""INSERT INTO shp.cdek_order_status (date_time, \
order_uuid, is_return, cdek_number, order_number, status_code, status_reason_code, status_date_time, city) \
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""

#class WebHookHandler(PGapp, log_app.LogApp):
class WebHookHandler():
    """
        Extract and write to PG the contents of the CDEK hook
    """
    #def __init__(self, pg_host, pg_user):
    def __init__(self, config):
        #gunicorn_err_logger = logging.getLogger('gunicorn.error')
        numeric_level = getattr(logging, config.LOG_LEVEL, None)

        log_format='[%(filename)-21s:%(lineno)4s - %(funcName)20s()] \
            %(levelname)-7s | %(asctime)-15s | %(message)s'
        #logging.basicConfig(stream=sys.stdout, format=log_format, level=config.LOG_LEVEL)
        if config.LOG_FILE is None or config.LOG_FILE == 'stdout':
            logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)
        else:
            logging.basicConfig(filename=config.LOG_FILE, format=log_format,\
                    level=numeric_level)
        logging.debug('level=%s', config.LOG_LEVEL)
        logging.debug('is_int=%s', isinstance(numeric_level, int))

        self.config = {}
        self.config['PG'] = {}
        self.config['PG']['pg_host'] = config.PG_HOST
        self.config['PG']['pg_user'] = config.PG_USER
        logging.debug('config=%s', self.config)
        self.jdata = None
        self.cur = None
        self.ins_sql = ''

    def parse_order_status(self):
        """ Parse JSON answer for ORDER_STATUS
        """
        self.ins_sql = self.cur.mogrify(INSERT_CDEK_STATUS,
                                      (self.jdata['date_time'],
                                       self.jdata['uuid'],
                                       self.jdata['attributes']['is_return'],
                                       self.jdata['attributes']['cdek_number'],
                                       self.jdata['attributes'].get('number'),
                                       self.jdata['attributes']['status_code'],
                                       self.jdata['attributes'].get('status_reason_code'),
                                       self.jdata['attributes']['status_date_time'],
                                       self.jdata['attributes'].get('city_name') #,
                                       #self.jdata['attributes']['code'],
                                       #self.jdata['attributes']['is_reverse'],
                                       #self.jdata['attributes']['is_client_return']
                                      )
                                     )

    def pg_write(self, arg_json):
        """
        Extract and write to PG the contents of the CDEK hook
        """
        self.jdata = arg_json

        try:
            #logging.error('config[PG][pg_host]=%s', self.config['PG']['pg_host'])
            #logging.error('config[PG][pg_user]=%s', self.config['PG']['pg_user'])
            con = psycopg2.connect(host=self.config['PG']['pg_host'],\
user=self.config['PG']['pg_user'])
        except psycopg2.Error as exc:
            #logging.error("Exception on connect=%s", sys.exc_info()[0])
            logging.error("Exception on connect=%s", exc)
        else:
            self.cur = con.cursor()
            if self.jdata['type'] == 'ORDER_STATUS':
                self.parse_order_status()
            else:
                self.ins_sql = ';'
            logging.info("SQL to execute=%s", str(self.ins_sql, encoding='UTF-8'))
            try:
                self.cur.execute(self.ins_sql)
            except psycopg2.Error:
                con.rollback()
                logging.error("Unexpected error:%s", sys.exc_info()[0])
            else:
                con.commit()
            con.close()


#ARGS = log_app.PARSER.parse_args()
app = Flask(__name__)
app.pg_writer = WebHookHandler(cdek_wh_config)
"""
app.pg_writer = WebHookHandler(pg_host=cdek_wh_config.PG_HOST,
                               pg_user=cdek_wh_config.PG_USER)
"""

@app.route('/', methods=['POST'])
def return_response():
    """ POST handler
    """
    if request.method == 'POST':
        #print(request.json)
        logging.debug('request.json=%s', json.dumps(request.json, ensure_ascii=False,
                                                    sort_keys=True,
                                                    indent=4))
        ## Extract and write to PG the contents of the CDEK hook
        app.pg_writer.pg_write(request.json)

    return Response(status=200)


if __name__ == "__main__":
    #log_app.PARSER.add_argument('--uuid', type=str, help='an order uuid to check status')
    app.run(host='192.168.1.101', debug=True, port=8123)
