from store.models import Customer, Order, OrderItem, Product , Collection
from django.conf import settings
from rest_framework import status
from django.db.models.aggregates import Count
from model_bakery import baker
from rest_framework.test import APIClient
import pytest


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/store/products/', product)
    return do_create_product

@pytest.fixture
def delete_product(api_client):
    def do_delete_product(product):
        return api_client.delete(f'/store/products/{product.id}/')
    return do_delete_product

@pytest.fixture
def patch_product(api_client):
    def do_patch_product(product, values):
        return api_client.patch(f'/store/products/{product.id}/', values) 
    return do_patch_product

@pytest.mark.django_db
class TestCreationProduct:
    def test_if_user_is_anonymous_returns_401(self, create_product):

        collection = baker.make(Collection)
        response = create_product({"title": "a",
                                    "description": "a",
                                    "slug": "-",
                                    "inventory": 4,
                                    "unit_price": 1,  
                                    "collection": collection.id,
                                    "images": []
                                })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_product):
        authenticate()

        collection = baker.make(Collection)
        response = create_product({"title": "a",
                                    "description": "a",
                                    "slug": "-",
                                    "inventory": 4,
                                    "unit_price": 1,  
                                    "collection": collection.id,
                                    "images": []
                                })

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self, authenticate, create_product):
        authenticate(is_staff = True ) 

        collection = baker.make(Collection)
        response = create_product({"title": "",
                                    "description": "a",
                                    "slug": "-",
                                    "inventory": 4,
                                    "unit_price": 0,  
                                    "collection": collection.id,
                                    "images": []
                                })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
        
    def test_if_data_is_valid_returns_201(self , authenticate, create_product):
        authenticate(is_staff = True)

        collection = baker.make(Collection)
        response = create_product({"title": "a",
                                    "description": "a",
                                    "slug": "-",
                                    "inventory": 4,
                                    "unit_price": 1,  
                                    "collection": collection.id,
                                    "images": []
                                })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_returns_200(self, api_client):
        #arrange
        product = baker.make(Product)
        #act
        response = api_client.get(f'/store/products/{product.id}/')
        #assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id
        assert response.data['title'] == product.title
        assert response.data['unit_price'] == product.unit_price
        assert response.data['collection'] == product.collection.id

    def test_if_product_does_not_exist_returns_404(self, api_client):

        response = api_client.get(f'/store/products/{-1}/')
        #assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
class TestDeleteProduct:
    def test_if_user_is_anonymous_returns_401(self,delete_product):
        product = baker.make(Product)

        response = delete_product(product)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self,authenticate ,delete_product):
        authenticate()
        product = baker.make(Product)

        response = delete_product(product)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_product_is_not_found_returns_404(self, authenticate, delete_product):
        authenticate(is_staff = True ) 

        response = delete_product(Product)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_product_is_deleted_returns_204(self,authenticate ,delete_product):
        authenticate(is_staff = True)
        product = baker.make(Product)

        response = delete_product(product)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Product.objects.all().count() == 0
    
    def test_if_product_is_an_order_item_returns_405(self,authenticate ,delete_product):
        authenticate(is_staff = True)
        product = baker.make(Product)
        user = baker.make(settings.AUTH_USER_MODEL)
        order = baker.make(Order, customer = user.customer)
        orderitem = baker.make(OrderItem, order = order , product=product)

        assert OrderItem.objects.all().count() > 0
        response = delete_product(product)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        
@pytest.mark.django_db
class TestUpdateProduct: 
    def test_if_user_is_anonymous_returns_401(self, patch_product):
        product = baker.make(Product)
    
        response = patch_product(product, {'title' : 'b', 'unit_price' : 11 })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, authenticate, patch_product):
        authenticate()
        product = baker.make(Product)
    
        response = patch_product(product, {'title' : 'b', 'unit_price' : 11 })

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self, authenticate, patch_product):
        authenticate(is_staff = True)
        product = baker.make(Product)
    
        response = patch_product(product, {'title' : '', 'unit_price' : 0 })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_200(self, authenticate, patch_product):
        authenticate(is_staff = True)
        product = baker.make(Product)
    
        response = patch_product(product, {'title' : 'a', 'unit_price' : 13 })

        assert response.status_code == status.HTTP_200_OK
        #product.refresh_from_db()
        assert response.data['id'] == product.id
        assert response.data['title'] == 'a'
        assert response.data['unit_price'] == 13
