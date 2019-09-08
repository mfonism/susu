import json

from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status

from ..models import User
from ..serializers import UserSerializer


class ListUserAPITest(APITestCase):

    def setUp(self):
        User.objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        User.objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        User.objects.create_user(
            email='ediomo@udofia.com', password='iamfabulous',
            first_name='Ediomo', last_name='Udofia'
        )
        User.objects.create_user(
            email='kim@essien.com', password='chubbybaby',
            first_name='Kim', last_name='Essien'
        )

    def test_list_users(self):
        # authenticated user can list users
        self.client.force_authenticate(User.objects.get(pk=1))

        url = reverse('user-list')
        response = self.client.get(url)

        serializer = UserSerializer(
            User.objects.all(),
            many=True,
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_list_users(self):
        url = reverse('user-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RetrieveUserAPITest(APITestCase):

    def setUp(self):
        self.mfon = User.objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.ambrose = User.objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )

    def test_retrieve_user(self):
        # authenticated user can retrieve self
        self.client.force_authenticate(self.mfon)

        url = reverse('user-detail', kwargs={'pk':self.mfon.pk})
        response = self.client.get(url)

        serializer = UserSerializer(
            self.mfon,
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_user_other_than_self(self):
        # authenticated user can retrieve some other user
        self.client.force_authenticate(self.mfon)

        url = reverse('user-detail', kwargs={'pk':self.ambrose.pk})
        response = self.client.get(url)

        serializer = UserSerializer(
            self.ambrose,
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_user(self):
        url = reverse('user-detail', kwargs={'pk':self.mfon.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UnallowedActionsUserAPITest(APITestCase):
    '''
    create, update and delete actions are not allowed from this endpoint.
    '''
    def setUp(self):
        self.mfon = User.objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )

    def test_cannot_create_from_this_endpoint(self):
        self.client.force_authenticate(self.mfon)

        url = reverse('user-list')
        valid_payload = {
            'email':'someone@gmail.com',
            'password':'somepassword'
            }

        response = self.client.post(
            url,
            data=json.dumps(valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_update_from_this_endpoint(self):
        self.client.force_authenticate(self.mfon)

        url = reverse('user-detail', kwargs={'pk': self.mfon.pk})
        valid_payload = {
            'email': self.mfon.email,
            'password': self.mfon.password
        }

        response = self.client.put(
            url,
            data=json.dumps(valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_delete_from_this_endpoint(self):
        self.client.force_authenticate(self.mfon)

        url = reverse('user-detail', kwargs={'pk': self.mfon.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
