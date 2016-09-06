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
            sendmail.send_mail('10.204.16.7', 'node DOWN report', 'c* cluster', 'calvin_chen@trendmicro.com.cn', b)
    except:
        sendmail.send_mail('10.204.16.7', 'node DOWN report-ERROR', 'c* cluster', 'calvin_chen@trendmicro.com.cn', "")
        logging.info("error occur!")


check_node_status()



