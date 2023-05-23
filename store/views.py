from distutils.sysconfig import customize_compiler
from itertools import product
from urllib import request
from venv import create
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin , RetrieveModelMixin, DestroyModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import  DjangoModelPermissions, IsAuthenticated , AllowAny, IsAdminUser

from store.permissions import IsAdminOrReadOnly , ViewCustomerHistoryPermission
from .filters import ProductFilter
from .pagination import DefaultPagination
from .models import Cart, CartItem, Collection, Customer, Order, Product, OrderItem, ProductImage, Review
from .serializers import AddCartItemSerializer, ProductImageSerializer, UpdateOrderSerializer , CartItemSerializer, CartSerializer, CollectionSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductSerializer, ReviewSerializer, UpdateCartItemSerializer
from store import serializers






# Create your views here.

# --( 5 )- here we are using "ModelViewSet" to combine [ ProductList ] -------
# ------- and [ProductDetail] in a single viewset called [ ProductViewSet ] --
# ------------- since they have multiple similar lines of code ---------------
# ----------------------------------------------------------------------------
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request': self.request}


    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product connot be deleted because it is associated with an order item.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)




# --- ( 4 ) ---- here we simply declare the class and its serializer--------
# ----- since we are not using some specific logic to handle the request ---
# --------------------------------------------------------------------------
# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#   def get_serializer_context(self):
#      return {'request': self.request}
#
#
#class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product connot be deleted because it is associated with an order item.'},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# --- ( 3 ) ---- here we are using Mixins / generics functionalities --
# -------------- and over wrote thier default functions ---------------
# ---------------------------------------------------------------------
# class ProductList(ListCreateAPIView):
#     # def get_queryset(self):
#     #     return Product.objects.select_related('collection').all()
#     # def get_serializer_class(self):
#     #     return ProductSerializer

#     def get_serializer_context(self):
#         return {'request': self.request}


# ---- ( 2 ) -- here we are using a Class inheriting from [APIview] Class
#-------------------------------------------------------------------------
#class ProductList(APIView):
    # def get(self, request):
    #     queryset = Product.objects.select_related('collection').all()
    #     serializer = ProductSerializer(
    #             queryset , many=True, context={'request': request})
    #     return Response(serializer.data)

    # def post(self, request):
    #     serializer = ProductSerializer(data = request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

# ----( 1 ) -- using functions as api view ----
#----------------------------------------------
# @api_view(['GET','POST'])
# def product_list(request):
#     if request.method == 'GET':
#         queryset = Product.objects.select_related('collection').all()
#         serializer = ProductSerializer(queryset , many=True, context={'request': request})
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = ProductSerializer(data = request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
            products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        if collection.products.count() > 0:
            return Response({'error': 'Collection connot be deleted because it is associated with an order item.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    #queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin,
                 DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects\
            .select_related('product').filter(cart_id=self.kwargs['cart_pk'])


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes = [ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('ok')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes = [IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id = request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        
class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post' ,'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
                data=request.data,
                context = {'user_id' : self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data) 


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    # def get_serializer_context(self):
    #     return {'user_id' : self.request.user.id}

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        
        customer_id = Customer.objects.only('id').get(user_id = user.id)
        return Order.objects.prefetch_related('items__product').filter(customer_id = customer_id)
    

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
