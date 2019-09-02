import json
from unittest import skip

from django.test import override_settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import User


@override_settings(AUTH_USER_MODEL='User')
class CreateUserTest(APITestCase):
    '''
    Test `POST`ing new user data to API.
    '''
    def setUp(self):
        self.valid_payload = {
            'email': 'mfon@etimfon.com',
            'password': 'notasecret, though!',
        }
        self.url = 'http://127.0.0.1:8000/auth/users/'

    def test_create_valid_user(self):
        response = self.client.post(
            path=self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCountEqual(response.data, {'id': 1, 'email': 'mfon'})

        self.assertEqual(User.objects.count(), 1)

    def test_cannot_create_invalid_user__no_email(self):
        response = self.client.post(
            path=self.url,
            data=json.dumps(self.valid_payload.update({'email':''})),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(User.objects.count(), 0)

    def test_cannot_create_invalid_user__no_password(self):
        response = self.client.post(
            path=self.url,
            data=json.dumps(self.valid_payload.update({'password':''})),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(User.objects.count(), 0)


@override_settings(AUTH_USER_MODEL='User')
class RetrieveAuthenticatedUserTest(APITestCase):
    '''
    Test `GET`ing the authenticated user.
    '''
    def setUp(self):
        self.mfon = User.objects.create_user(
            email='mfon@etimfon.com', password='notstrong'
        )
        self.url = 'http://127.0.0.1:8000/auth/users/me/'

    def test_retrieve_authenticated_user(self):
        self.client.force_authenticate(user=self.mfon)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, {'id': self.mfon.pk, 'email': self.mfon.email})

    def test_cannot_retrieve_unathenticated_user(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(AUTH_USER_MODEL='User')
class UpdateAuthenticatedUserTest(APITestCase):
    '''
    Test `PUT`ing at authenticated user's uri.
    '''
    def setUp(self):
        self.url = 'http://127.0.0.1:8000/auth/users/me/'

    def test_email_field_does_not_get_updated(self):
        old_email = 'mfon@etimfon.com'
        new_email = 'mfon@esusuconfam.com'
        mfon = User.objects.create_user(email=old_email, password='nopassword')

        self.client.force_authenticate(user=mfon)
        response = self.client.put(
            path=self.url,
            data=json.dumps({'email': new_email}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, {'id': mfon.pk, 'email': old_email})

    def test_cannot_update_unathenticated_user(self):
        mfon = User.objects.create_user(email='mfon@etimfon.com', password='nopassword')

        # forced authentication line absent
        response = self.client.put(
            path=self.url,
            data=json.dumps({'email': 'mfon@esusuconfam.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @skip('in our case User.REQUIRED_FIELDS is empty ' \
          'so we can\'t exactly test for this.')  
    def test_cannot_update_missing_required_field(self):
        '''Should complain with HTTP_400_BAD_REQUEST.'''
        pass
        