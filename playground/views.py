from cgitb import reset
import collections
from decimal import Decimal
from distutils.util import execute 
from unittest import result
from winreg import QueryInfoKey
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q , F , Func , ExpressionWrapper
from store.models import Product , Customer, Order, OrderItem, Collection
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Count, Max, Min, Avg,Sum
from django.db.models import Value, DecimalField
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from tags.models import TaggedItem
from django.db import transaction
from django.db import connection
from django.core.mail import send_mail, mail_admins, BadHeaderError
from .tasks import notify_customers

# Create your views here.

def say_hello(request):
    notify_customers.delay('Hello from the other side!')
    return render(request,'hello.html', {'name': 'Yas / Sir'})



    # queryset = Order.objects.filter(customer__id=1)


    # return render(request,'hello.html', {'name': 'Yas / Sir', 'result': list(queryset) })
        # with transaction.atomic():
        #     order = Order()
        #     order.customer_id = 1
        #     order.save()

        #     item = OrderItem()
        #     item.order = order
        #     item.product_id = 1
        #     item.quantity = 2
        #     item.unit_price = 20
        #     item.save()
        # return render(request,'hello.html', {'name': 'Yas / Sir' })



        #collection = Collection.objects.get(pk=10)
        #collection.featured_product = None
        #collection.save()
        
        #queryset =  TaggedItem.objects.get_tags_for(Product, 1)        
        #return render(request,'hello.html', {'name': 'Yas / Sir' })

    #discounted_price =ExpressionWrapper(F('unit_price') * 0.8, output_field= DecimalField())
    #queryset = Product.objects.annotate(discount_price = discounted_price)
    #result = Customer.objects.annotate(is_new=F('id') + 10)
    #result = Product.objects.filter(collection__id=3).aggregate(Max_unit_price = Max('unit_price'), Avg_unit_price = Avg('unit_price') , Min_unit_price = Min('unit_price'))
    #result = Order.objects.filter(customer__id=1).aggregate(order_placed= Count('id'))
    #result = OrderItem.objects.filter(product__id=1).aggregate(unit_sold = Sum('quantity'))
    #result = Product.objects.aggregate(Count('id'))
    #####

    #queryset = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    # select_related(1)
    # prefetch_related(n)
    #queryset = Product.objects.prefetch_related('promotions').select_related('collection').all()
    #queryset = Product.objects.select_related('collection').all()
    #queryset = Product.objects.only('id','title','unit_price')
    #queryset = Product.objects.filter(id__in = OrderItem.objects.values('product_id').distinct())    
    #queryset = Product.objects.values_list('id', 'title' , 'collection__title')
    #queryset = Product.objects.order_by('unit_price')[0:4]

    #queryset = Product.objects.filter(inventory = F('unit_price'))
    # Products : inventory < 10 OR price < 20
    #queryset = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=10) )
    #queryset = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=10)

    #queryset = Collection.objects.filter(featured_product__isnull= True)
    #queryset = OrderItem.objects.filter(product__collection__id=3)
    #queryset = Order.objects.filter(customer__pk=1)
    #queryset = Product.objects.filter(inventory__lt=10)
    #queryset = Customer.objects.filter(email__icontains = ".com")
    
        

    #return render(request,'hello.html', {'name': 'Yas / Sir', 'result' : queryset })
