from store.models import Collection, Product
from rest_framework import status
#from django.db.models.aggregates import Count
from model_bakery import baker
import pytest

@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return do_create_collection

@pytest.fixture
def delete_collection(api_client):
    def do_delete_collection(collection):
        return api_client.delete(f'/store/collections/{collection.id}/')
    return do_delete_collection

@pytest.fixture
def patch_collection(api_client):
    def do_patch_collection(collection, value):
        return api_client.patch(f'/store/collections/{collection.id}/', value) 
    return do_patch_collection


# @pytest.mark.django_db
# class TestCreateCollections:
#     def test_if_user_is_anonymous_returns_401(self):
#         # Arrange
#             #empty
#         #Act
#         client = APIClient()
#         response = client.post('/store/collections/', {'title' : 'a'})
#         # Assert
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED
@pytest.mark.django_db
class TestCreateCollections:
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        response = create_collection({'title' : 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, authenticate, create_collection):
        authenticate()

        response = create_collection({'title' : 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self, authenticate, create_collection):
        authenticate(is_staff = True ) 

        response = create_collection({'title' : ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, authenticate, create_collection):
        authenticate(is_staff = True) 

        response = create_collection({'title' : 'a'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        #arrange
        collection = baker.make(Collection)
        #act
        response = api_client.get(f'/store/collections/{collection.id}/')
        #assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == collection.id
        assert response.data['title'] == collection.title
    
    def test_if_collection_exists_returns_200(self, api_client):

        response = api_client.get(f'/store/collections/{1}/')
        #assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteCollection:
    def test_if_user_is_anonymous_returns_401(self, delete_collection):
        #arrange
        collection = baker.make(Collection)
        #assert
        response = delete_collection(collection)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, authenticate, delete_collection):
        authenticate()

        collection = baker.make(Collection)

        response = delete_collection(collection)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_collection_is_not_found_returns_404(self, authenticate, delete_collection):
        authenticate(is_staff = True ) 
        
        response = delete_collection(Collection)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_user_is_admin_and_deleted_returns_204(self, authenticate, delete_collection):
        authenticate(is_staff = True ) 
        #arrange
        collection = baker.make(Collection)
        #assert
        response = delete_collection(collection)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        response = delete_collection(collection)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_if_collection_is_not_empty_returns_405(self, authenticate, delete_collection):
        authenticate(is_staff = True ) 
        #arrange
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)
        #assert
        assert collection.products.count() > 0
        response = delete_collection(collection)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        

        
@pytest.mark.django_db       
class TestUpdateCollection:
    def test_if_user_is_anonymous_returns_401(self, patch_collection):
        collection = baker.make(Collection)

        response = patch_collection(collection, {'title' : 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self,authenticate,patch_collection):
        authenticate()
        collection = baker.make(Collection)

        response = patch_collection(collection, {'title' : 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self,authenticate, patch_collection):
        authenticate(is_staff = True)
        collection = baker.make(Collection)

        response = patch_collection(collection, {'title' : ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_user_is_admin_returns_200(self,authenticate, patch_collection):
        authenticate(is_staff = True)
        collection = baker.make(Collection)

        response = patch_collection(collection, {'title' : 'a'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == collection.id
        assert response.data['title'] == 'a'
        
        

