import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import time
import os


class Foxmail():
    def __init__(self, foxmail_addr, pwd, debuglevel=0):
        self.foxmail_addr = foxmail_addr
        self.pwd = pwd
        self.mail_host = 'smtp.qq.com'
        self.debuglevel = debuglevel

    def set_msg(self, subject, content):
        self.msg = MIMEMultipart()
        self.msg_subject = str(subject)
        self.msg_content = str(content)
        self.msg['From'] = self.foxmail_addr
        self.msg['Subject'] = self.msg_subject
        self.msg.attach(MIMEText(self.msg_content, 'plain', 'utf-8'))

    def set_receivers(self, receivers):
        if type(receivers) == str:
            self.receivers = [receivers]
        else:
            self.receivers = receivers

    def set_attachments(self, attachments):
        if type(attachments) == str:
            self.msg_attachments = [attachments]
        else:
            self.msg_attachments = attachments
        for file in self.msg_attachments[:]:
            try:
                with open(file, 'rb') as f:
                    file_name = os.path.basename(file)
                    attr = MIMEText(f.read(), 'base64', 'utf-8')
                    attr["Content-Type"] = 'application/octet-stream'
                    attr[
                        "Content-Disposition"] = 'attachment; filename="%s"' % file_name
                    self.msg.attach(attr)
            except FileNotFoundError:
                self.msg_attachments.remove(file)
                current_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime())
                print("%s [JOEYLYU] File %s not found!" % (current_time, file))

    def login(self):
        self.smtp = smtplib.SMTP_SSL(self.mail_host, 465)
        self.smtp.set_debuglevel(self.debuglevel)
        self.smtp.login(self.foxmail_addr, self.pwd)

    def info(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("%s [JOEYLYU] Send Account: %s" %
              (current_time, self.foxmail_addr))
        print("%s [JOEYLYU] Receive Account: %s" %
              (current_time, str(self.receivers)))
        print("%s [JOEYLYU] Message Subject: %s" %
              (current_time, self.msg_subject))
        print("%s [JOEYLYU] Message Content: %s" %
              (current_time, self.msg_content))
        print("%s [JOEYLYU] Message Attachments: %s" %
              (current_time, str(self.msg_attachments)))

    def send(self):
        try:
            self.info()
            self.login()
            for receiver in self.receivers:
                self.msg['To'] = receiver
                self.smtp.sendmail(self.foxmail_addr, receiver,
                                   self.msg.as_string())
                current_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime())
                print("%s [JOEYLYU] %s" % (current_time, "EMAIL SENT!"))
        except smtplib.SMTPException as e:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("%s [JOEYLYU] Email sent failed %s" % (current_time, e))


# Example
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    foxmail_addr = 'lvliangxiong@foxmail.com'
    # QQ authorization code
    passWord = 'xyjzjnlulvxqbbfi'
    # mail addr you want to send
    receivers = ['lvliangxiong@foxmail.com']
    msg_attachments = ["test.json", "test2.json"]

    msg_subject = input("Email Subject: ")
    msg_content = input("Email Content: ")

    fm = Foxmail(foxmail_addr, passWord)
    fm.set_msg(msg_subject, msg_content)
    fm.set_attachments(msg_attachments)
    fm.set_receivers(receivers)
    fm.send()
