#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.la.bot2py
====================================
.. moduleauthor:: Raven Lim <deokyu@argos-labs.com>
.. note:: VIVANS License

Description
===========
ARGOS LABS PAM For LA

Authors
===========

* Raven Lim

Change Log
--------

 * [2019/01/30]
    - starting
"""

################################################################################
import sys
import socket
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from alabs.common.util.vvargs import ModuleContext, func_log
from alabs.common.util.vvlogger import StructureLogFormat



################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['windows', 'darwin', 'linux']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'



################################################################################
@func_log
def send_email(mcxt, argspec):
    """
    LocateImage
    :param mcxt: module context
    :param argspec: argument spec
    :return: x, y
    """
    mcxt.logger.info("Send Email start ...")

    status = True
    message = ''
    try:
        receiver_emails = list()
        receiver_emails += argspec.to.split(',')
        if argspec.bcc:
            receiver_emails += argspec.bcc.split(',')
        if argspec.cc:
            message["Cc"] = argspec.cc
            receiver_emails += argspec.cc.split(',')

        subject = argspec.subject
        body = argspec.content
        sender_email = argspec.mail_address
        password = argspec.password
        smtp_server = argspec.smtp_host
        smtp_port = argspec.smtp_port

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = argspec.to
        message["Subject"] = subject

        # plain/html 형태로 내용 형태 지정
        part1 = MIMEText(body, "plain")
        message.attach(part1)

        # 파일첨부
        attaches = argspec.attach if argspec.attach else list()
        for attach in attaches:
            filename = attach
            # Open PDF file in binary mode
            with open(filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)

            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            message.attach(part)

        text = message.as_string()

        if argspec.ssl:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_emails, text)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_emails, text)
    except socket.gaierror as e:
        status = False
        mcxt.logger.exception(str(e))
        message = "SMTP server address is wrong. Check the address. "

    except ConnectionRefusedError as e:
        status = False
        mcxt.logger.exception(str(e))
        message = "Connection to SMTP server refused. " \
                  "Check the port number or firewall."

    except smtplib.SMTPAuthenticationError as e:
        status = False
        mcxt.logger.exception(str(e))
        message = "Authentication Failed. Check the ID or Password."

    except Exception as e:
        status = False
        mcxt.logger.exception(str(e))
        message = str(e)

    if isinstance(message, email.mime.multipart.MIMEMultipart):
        message = message.values()

    result = StructureLogFormat(RETURN_CODE=status,
                                RETURN_VALUE={'RESULT': status},
                                MESSAGE=message)
    std = {True: sys.stdout, False: sys.stderr}[status]
    std.write(str(result))

    mcxt.logger.info("Send Email end ...")
    return result


################################################################################
def _main(*args):
    """
    Build user argument and options and call plugin job function
    :param args: user arguments
    :return: return value from plugin job function

    ..note:: _main 함수에서 사용되는 패러미터(옵션) 정의 방법
플러그인 모듈은 ModuleContext 을 생성하여 mcxt를 with 문과 함께 사용
    owner='ARGOS-LABS',
    group='pam',
    version='1.0',
    platform=['windows', 'darwin', 'linux'],
    output_type='text',
    description='HA Bot for LA',
    test_class=TU,
    """
    with ModuleContext(
        owner=OWNER,
        group=GROUP,
        version=VERSION,
        platform=PLATFORM,
        output_type=OUTPUT_TYPE,
        description=DESCRIPTION,
    ) as mcxt:
        # 'python -m alabs.pam.rpa.desktop.send_email ' \
        # 'mail2.vivans.net 25 ' \
        # 'deokyu@vivans.net vivans123$ ' \
        # 'deokyu@vivans.net ' \
        # '"deokyu@argos-labs.com,deokyu@vivans.net" ' \
        # 'HelloThere4 "Hello World!!!!!" ' \
        # '--cc "hong18s@gmail.com" ' \
        # '--bcc "im.ddo.lee@gmail.com" ' \
        # '--attach .env --attach .gitignre'

        # 필수 입력 항목
        mcxt.add_argument('smtp_host', type=str, help='')
        mcxt.add_argument('smtp_port', type=int, help='')
        mcxt.add_argument('id', type=str, help='')
        mcxt.add_argument('password', type=str, help='')
        mcxt.add_argument('mail_address', type=str, help='')

        mcxt.add_argument('to', type=str, help='')
        mcxt.add_argument('subject', type=str, help='')
        mcxt.add_argument('content', type=str, help='')
        mcxt.add_argument('--cc', type=str, help='')
        mcxt.add_argument('--bcc', type=str, help='')
        mcxt.add_argument('--attach', type=str, action='append', help='')

        mcxt.add_argument('--ssl', action='store_true', help='')

        argspec = mcxt.parse_args(args)
        return send_email(mcxt, argspec)


################################################################################
def main(*args):
    return _main(*args)

