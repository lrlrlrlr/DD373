from email.mime.text import MIMEText

msg = MIMEText('hello, send by python.', 'plain', 'utf-8')

from_addr = input('From:  ')
password = input('Passwd:  ')

to_addr = input('To:  ')
smtp_server = input('SMTP server:  ')

import smtplib

server = smtplib.SMTP(smtp_server, 25)
server.set_debuglevel(1)
server.login(from_addr, password)
server.sendmail(from_addr, [to_addr], msg.as_string())
server.quit()
