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

    + Email and password fields must be present and valid
    + Fields in <user_model>.REQUIRED_FIELDS must be present, too
    '''
    def setUp(self):
        self.valid_payload = {
            'email': 'mfon@etimfon.com',
            'password': 'notasecret, though!',
        }
        self.url = 'http://127.0.0.1:8000/auth/users/'

    def test_create_user(self):
        # create user with email and password
        # (amongst all required fields)
        response = self.client.post(
            path=self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(response.data, {'id': 1, 'email': 'mfon@etimfon.com'})

        self.assertEqual(User.objects.count(), 1)

    def test_create_user__no_email(self):
        # cannot create user with an empty email
        response = self.client.post(
            path=self.url,
            data=json.dumps(self.valid_payload.update({'email':''})),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(User.objects.count(), 0)

    def test_create_user__no_password(self):
        # cannot create user with an empty password
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

    + Users will always only get themselves
    + Only authenticated users can get
    '''
    def setUp(self):
        self.mfon = User.objects.create_user(
            email='mfon@etimfon.com', password='notstrong'
        )
        self.url = 'http://127.0.0.1:8000/auth/users/me/'

    def test_retrieve_user(self):
        # authenticated users can get
        self.client.force_authenticate(user=self.mfon)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {'id': self.mfon.pk, 'email': self.mfon.email})

    def test_retrieve_user__unathenticated(self):
        # unauthenticated users are not authorised to get
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(AUTH_USER_MODEL='User')
class UpdateAuthenticatedUserTest(APITestCase):
    '''
    Test `PUT`ing at authenticated user's uri.

    + Users will always only update themselves
    + Only authenticated users can update
    '''
    def setUp(self):
        self.url = 'http://127.0.0.1:8000/auth/users/me/'

    def test_email_field_does_not_get_updated(self):
        # email fields cannot be updated via this view
        # password fields, too
        old_email = 'mfon@etimfon.com'
        new_email = 'mfon@esusuconfam.com'
        mfon = User.objects.create_user(
                    email=old_email, password='nopassword'
                )

        self.client.force_authenticate(user=mfon)
        response = self.client.put(
            path=self.url,
            data=json.dumps({'email': new_email}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {'id': mfon.pk, 'email': old_email})

    def test_update__unathenticated_user(self):
        # unathenticated user is not authorized to update
        mfon = User.objects.create_user(
                    email='mfon@etimfon.com', password='nopassword'
                )

        # forced authentication line absent
        response = self.client.put(
            path=self.url,
            data=json.dumps({'email': 'mfon@esusuconfam.com'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @skip('in our case User.REQUIRED_FIELDS is empty ' \
          'so we can\'t exactly test for this.')  
    def test_update__missing_required_field(self):
        '''Should complain with HTTP_400_BAD_REQUEST.'''
        pass


@override_settings(AUTH_USER_MODEL='User')
class DeleteAuthenticatedUserTest(APITestCase):
    '''
    Test `DELETE`ing currently authenticated user.

    + Users can only delete themselves
    + Only authenticated users can delete
    + The correct password of the user must be supplied to delete
    '''
    def setUp(self):
        self.mfon = User.objects.create_user(
                    email='mfon@etimfon.com', password='4g8menut'
                )
        self.url = 'http://127.0.0.1:8000/auth/users/me/'

    def test_delete__authenticated_user(self):
        # authentiated user can delete self with correct current password
        self.client.force_authenticate(user=self.mfon)
        response = self.client.delete(
            path=self.url,
            data=json.dumps({'current_password': '4g8menut'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete__authenticated_user__wrong_password(self):
        # authenticated user can't delete self with wrong password
        self.client.force_authenticate(user=self.mfon)
        response = self.client.delete(
            path=self.url,
            data=json.dumps({'current_password': 'forgotten'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete__unauthenticated_user(self):
        # unathenticated user is not authorized to delete
        response = self.client.delete(
            path=self.url,
            data=json.dumps({'current_password': '4g8menut'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
