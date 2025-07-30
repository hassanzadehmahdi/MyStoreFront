from time import sleep
from celery import shared_task

@shared_task
def notify_customers(message):
    print('Notifying customers...')
    print('Message: {}'.format(message))
    sleep(10)
    print('Customer notified!')
