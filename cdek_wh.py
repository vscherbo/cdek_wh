#!/usr/bin/env python
""" CDEK webhooks listener
gunicorn -w 2 -b 0.0.0.0:3000 myapp:app
"""

import sys
import logging
import time
import json

from flask import Flask, request, Response
import psycopg2

import cdek_wh_config

INSERT_CDEK_STATUS = u"""INSERT INTO shp.cdek_order_status (date_time, order_uuid, is_return, \
cdek_number, order_number, status_code, status_reason_code, status_date_time, city, code, is_reverse, is_client_return) \
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

INSERT_PRINT_FORM = u"""INSERT INTO shp.cdek_print_form (date_time, order_uuid, form_type, url) \
VALUES (%s, %s, %s, %s);"""

#class WebHookHandler(PGapp, log_app.LogApp):
class WebHookHandler():
    """
        Extract and write to PG the contents of the CDEK hook
    """
    def __init__(self, config):
        numeric_level = getattr(logging, config.LOG_LEVEL, None)

        log_format='[%(filename)-21s:%(lineno)4s - %(funcName)20s()] \
            %(levelname)-7s | %(asctime)-15s | %(message)s'
        if config.LOG_FILE is None or config.LOG_FILE == 'stdout':
            logging.basicConfig(stream=sys.stdout, format=log_format, level=numeric_level)
        else:
            logging.basicConfig(filename=config.LOG_FILE, format=log_format,\
                    level=numeric_level)
        logging.debug('level=%s', config.LOG_LEVEL)
        logging.debug('is_int=%s', isinstance(numeric_level, int))

        self.pg_host = config.PG_HOST
        self.pg_user = config.PG_USER
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
                                       self.jdata['attributes'].get('city_name'),
                                       self.jdata['attributes']['code'],
                                       self.jdata['attributes']['is_reverse'],
                                       self.jdata['attributes']['is_client_return']
                                      )
                                     )

    def parse_print_form(self):
        """ Parse JSON answer for PRINT_FORM
        """
        time.sleep(5)
        self.ins_sql = self.cur.mogrify(INSERT_PRINT_FORM,
                                      (self.jdata['date_time'],
                                       self.jdata['uuid'],
                                       self.jdata['attributes']['type'],
                                       self.jdata['attributes']['url']
                                      )
                                     )

    def pg_write(self, arg_json):
        """
        Extract and write to PG the contents of the CDEK hook
        """
        self.jdata = arg_json

        try:
            con = psycopg2.connect(host=self.pg_host, user=self.pg_user,
                    connect_timeout=30)
        except psycopg2.Error as exc:
            logging.error("Exception on connect=%s", exc)
        else:
            self.cur = con.cursor()
            # prepare SQL and write to log
            if self.jdata['type'] == 'ORDER_STATUS':
                self.parse_order_status()
            elif self.jdata['type'] == 'PRINT_FORM':
                self.parse_print_form()
            logging.info("SQL to execute=%s", str(self.ins_sql, encoding='UTF-8'))
            try:
                self.cur.execute(self.ins_sql)
            except psycopg2.Error:
                con.rollback()
                logging.error("psycopg2.Error: %s", sys.exc_info())
            else:
                con.commit()
            con.close()


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
        logging.debug('request.json=%s', json.dumps(request.json, ensure_ascii=False,
                                                    sort_keys=True,
                                                    indent=4))
        ## Extract and write to PG the contents of the CDEK hook
        app.pg_writer.pg_write(request.json)

    return Response(status=200)


if __name__ == "__main__":
    app.run(host='192.168.1.101', debug=True, port=8123)
