import pytest
from rest_framework import status
from model_bakery import baker
from store.models import Collection

@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return do_create_collection


@pytest.mark.django_db
class TestCreateCollections():

    # @pytest.mark.skip
    def test_if_user_is_anonymous_return_401(self, create_collection):
        # Arrange

        # Act
        response = create_collection({'title': 'Test Collection'})

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_return_403(self, authenticate, create_collection):
        # Arrange
        authenticate(is_staff=False)

        # Act
        response = create_collection({'title': 'Test Collection'})

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_if_data_is_invalid_return_400(self, authenticate, create_collection):
        # Arrange
        authenticate(is_staff=True)

        # Act
        response = create_collection({'title': ''})

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get('title') is not None


    def test_if_data_is_valid_return_201(self, authenticate, create_collection):
        # Arrange
        authenticate(is_staff=True)

        # Act
        response = create_collection({'title': 'Test Collection'})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('id') > 0


@pytest.mark.django_db
class TestRetrieveCollections():
    def test_if_collection_exists_returns_200(self, api_client):
        # Arrange
        collections = baker.make(Collection)

        # Act
        response = api_client.get(f'/store/collections/{collections.id}/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collections.id,
            'title': collections.title,
            'products_count': 0,
        }



#########################################################
# old code

    # def test_if_user_is_anonymous_return_401(self):
    #     # Arrange
    #
    #     # Act
    #     client = APIClient()
    #     response = client.post('/store/collections/', {'title': 'Test Collection'})
    #
    #     # Assert
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED