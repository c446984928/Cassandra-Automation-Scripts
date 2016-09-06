# -*- coding: utf-8 -*-
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import socket
import sys


# default
g_server="10.204.16.7"
g_subject = "Cassandra node update report"
g_sender=""
g_receiver="calvin_chen@trendmicro.com.cn"
g_body=""
logging.basicConfig(filename='./run.log',
                    level=logging.DEBUG, filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s')


def get_my_ip():
    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def send_mail(server,subject,sender,receiver,body):
    # username = ''
    # password = ''
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    try:
        smtp = smtplib.SMTP()
        smtp.connect(server, "25")
        # smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        logging.info(server+subject+sender+receiver+body)
        smtp.quit()
    except Exception, e:
        logging.error("Send Mail Error",e)


def sendmail(subject=g_subject,receiver=g_receiver):
    sender=get_my_ip()
    send_mail(g_server,subject,sender,receiver,g_body)


if __name__ == '__main__':
    # no params:all default
    # 1  params: object
    # 2  params: object + receiver
    params = sys.argv
    g_sender=get_my_ip()
    if len(params)==1:
        send_mail(g_server,g_subject,g_sender,g_receiver,g_body)
    elif len(params)==2:
        send_mail(g_server,params[1],g_sender,g_receiver,g_body)
    elif len(params)==3:
        send_mail(g_server,params[1],g_sender,params[2],g_body)
