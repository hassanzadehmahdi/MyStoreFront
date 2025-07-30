import logging
import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q, F
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from templated_mail.mail import BaseEmailMessage

from playground.tasks import notify_customers
from store.models import Product, OrderItem, Order, OrderItem
from tags.models import Tag, TaggedItem

# Create your views here.
# @cache_page(5 * 60)
# def index(request):
    ### querying from database
    # query_set = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
    # query_set = Product.objects.filter(Q(inventory__gt=10) | ~Q(inventory__lt=20))
    # query_set = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')
    # query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[0:5]
    # query_set = TaggedItem.objects.get_tags_for(Product, 1)

    ### sending emails
    # try:
        ### send email to normal users
        # send_mail('subject', 'message', 'mahdi@gmail.com', ['hadi@gamil.com'])

        ### send email to admins
        # mail_admins('subject', 'message', '', html_message='message')

        ### attach file
        # message = EmailMessage('subject', 'message', 'mahdi@gmail.com', ['hadi@gmail.com'])
        # message.attach_file('playground/statics/images/fyvkr93-public.png')
        # message.send()

        ### sending templated email
    #     message = BaseEmailMessage(
    #         template_name='emails/hello.html',
    #         context={'name': 'mahdi'},
    #     )
    #     message.send(to=['mahdi@gmail.com'], from_email='hadi@gmail.com')
    # except BadHeaderError:
    #     return HttpResponse('Invalid header found.')

    ### running tasks and Celery stuff
    # notify_customers.delay('hello world')

    ### caching data manually
    # key = 'httpbin_result'
    # if key not in cache:
    #     response = requests.get('https://httpbin.org/delay/2')
    #     data = response.json()
    #     cache.set(key, data)

    ### caching data with cache_page decorator
    # response = requests.get('https://httpbin.org/delay/2')
    # data = response.json()
    #
    #
    # return render(request, 'index.html', context={'name': data})
    #


### logging
logger = logging.getLogger(__name__) # playground.views

class HelloView(APIView):

    @method_decorator(cache_page(1 * 60))
    def get(self, request):
        try:
            logger.info('Calling HttpBin.')
            response = requests.get('https://httpbin.org/delay/2')
            logger.info('Response from HttpBin received.')
            # data = response.json()
        except requests.ConnectionError as e:
            logger.critical('Connection error with HttpBin: %s', e)

        return render(request, 'playground/index.html', context={'name': 'data'})
