#! /usr/bin/env python
#coding=utf-8

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
from flask import current_app
import random


class Mail(object):
    def __init__(self):
        """ 配置文件路径: main/conf/flask/private/private.py """

        self.server = current_app.config.get('MAIL_SERVER')
        self.port = current_app.config.get('MAIL_PROT')
        self.ssl = current_app.config.get('MAIL_USE_SSL')
        self.usernema = current_app.config.get('MAIL_USERNAME')
        self.password = current_app.config.get('MAIL_PASSWORD')
        self.debug = current_app.config.get('MAIL_DEBUG')

    def send_verified_code(self, receiver):
        """
        发送验证码
        """
        title = "您在二猫子博客的验证码 ฅ(=ↀωↀ=)ฅ"
        verified_code = "".join(map(str, random.sample(range(9), 6)))
        content = f"您好!<br>虽然并不知道您在做什么, 但突然收到命令, 需要在此刻给您发送一个验证码: <br>" \
                  f"<h1>{verified_code}</h1><br>上面就是您的验证码了, 为了您的账号安全请不要将其外泄<br><br><h5>毕竟我们这个小破站全是破绽 Ծ‸Ծ</h5>"
        self.send_email(receiver, title, content)

    def send_email(self, receiver, title, content):

        if self.ssl:
            smtp = smtplib.SMTP_SSL(self.server, self.port)
        else:
            smtp = smtplib.SMTP(self.server, self.port)

        if self.debug:
            smtp.set_debuglevel(1)

        smtp.ehlo(self.server)
        smtp.login(self.usernema, self.password)

        mail_body = MIMEText(content, _subtype='html', _charset='utf-8')

        msg = MIMEMultipart()
        msg.attach(mail_body)
        msg["Subject"] = Header(title, 'utf-8')
        msg["From"] = self.usernema
        msg["To"] = receiver
        smtp.sendmail(self.usernema, receiver, msg.as_string())
        smtp.quit()
