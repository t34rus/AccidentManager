import re
import poplib
import email
from email import parser

def getmails():
    pop3 = poplib.POP3_SSL('pop.mail.ru')
    pop3.user('noreplysup@mail.ru')
    pop3.pass_('fdnjvfn')
    #Get messages from server:
    mcount=len(pop3.list()[1])
    for i in range(1,mcount):
        msg=pop3.retr(i+1)
        raw_mail='\n'.join(msg[1])
        mail=email.message_from_string(raw_mail)

        # subject
        subject = mail.get('Subject')
        h = email.header.decode_header(subject)
        msg = h[0][0].decode(h[0][1]) if h[0][1] else h[0][0]
        print(msg)
    pop3.quit()

from Scheduler import *
#scheduler.add_job(getmails, 'interval', seconds=1)
