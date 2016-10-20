# -*- coding: utf-8 -*-
import commands
import logging
import os
import sendmail

PATH = "/Project/apache-cassandra-3.0.6/bin/nodetool status"
logging.basicConfig(filename='./run.log',
                    level=logging.DEBUG, filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s')


def check_node_status():
    try:
        b = commands.getoutput(PATH)
        logging.info(b)
        if "DN" in b or "Status=Up/Down" not in b:
            if read_flag() == 'normal':
                write_flag('abnormal')
                send_mail_tool(b)
            elif read_flag() == 'abnormal':
                pass
            else:
                write_flag('abnormal')
                send_mail_tool(b)

        else:
            write_flag('normal')

    except:
        send_mail_tool("Check node status error!")


def write_flag(flag):
    with open('status.flag', 'w') as f:
        f.write(flag)


def read_flag():
    if os.path.isfile('status.flag'):
        with open('status.flag', 'r') as f:
            flag_str = f.readline()
            if 'abnormal' in flag_str:
                return 'abnormal'
            else:
                return 'normal'
    else:
        return 'normal'


def send_mail_tool(b):
    logging.info("sendmail")
    sendmail.send_mail('10.204.16.7', 'node DOWN report', 'c* cluster', 'a@test.com', b)
    sendmail.send_mail('10.204.16.7', 'node DOWN report', 'c* cluster', 'b@test.com', b)


check_node_status()
