import re
import poplib
import email


def getmails():
    import sys
    pop3 = poplib.POP3_SSL('pop.mail.ru')
    print(pop3.getwelcome())
    pop3.user('noreplysup@mail.ru')
    pop3.pass_('fdnjvfn')
    #Get messages from server:
    pop3.list()
    (numMsgs, totalSize) = pop3.stat()
    for i in range(1, numMsgs + 1):
        response  = pop3.retr(i)
        # return in format: (response, ['line', ...], octets)
        raw_message = response[1]
        for msg in raw_message:
            if email.message_from_bytes(msg).startswith('Subject'):
                print ('\t' + msg)
        str_message = email.message_from_bytes(b'\n'.join(raw_message))
        print(str_message.get_subject())
        for part in str_message.walk():
            print(part.get_content_type())
            if part.get_content_type() == 'text/plain':
                body = part.get_payload()
                #print(body)
        print('-----------------------')
    pop3.quit()

from Scheduler import *
#scheduler.add_job(getmails, 'interval', seconds=1)
