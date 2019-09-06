import json

from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.exceptions import ErrorDetail

from ..views import EsusuGroupViewSet
from ..models import EsusuGroup
from ..serializers import EsusuGroupSerializer


class EsusuGroupListApiTest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            email='mfon@etimfon.com', password='4g8menut!'
        )
        EsusuGroup.objects.create(name='First Group', admin=self.user)
        EsusuGroup.objects.create(name='Second Group', admin=self.user)
        EsusuGroup.objects.create(name='Third Group', admin=self.user)
        EsusuGroup.objects.create(name='Fourth Group', admin=self.user)

    def test_list_group(self):        
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-list')
        response = self.client.get(url)

        # we need to supply the serializer a request
        # because it is a hyperlinked serializer
        # and needs a request to build urls from
        serializer = EsusuGroupSerializer(
            EsusuGroup.objects.all(),
            many=True,
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertTrue(EsusuGroup.objects.all().exists())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_list_group(self):
        url = reverse('esusugroup-list')
        response = self.client.get(url)
        expected_response_data = {
            'detail': ErrorDetail(
                        'Authentication credentials were not provided.',
                        code='not_authenticated'
                    )
        }

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertDictEqual(response.data, expected_response_data)


class EsusuGroupCreateApiTest(APITestCase):

    def setUp(self):
        get_user_model().objects.create(
            email='itoro@etimfon.com', password='nopassword'
        )
        self.user = get_user_model().objects.create(
            email='mfon@etimfon.com', password='4g8menut!'
        )
        self.valid_payload = {
            'name': 'Lifelong Savers',
        }

    def test_create_group(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-list')
        response = self.client.post(
            url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        esusugroup = EsusuGroup.objects.get(pk=1)
        serializer = EsusuGroupSerializer(
            esusugroup,
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertEqual(esusugroup.admin.pk, self.user.pk)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_cannot_create_group_with_invalid_payload(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-list')
        response = self.client.post(
            url,
            data=json.dumps({'name':''}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_create_group(self):
        url = reverse('esusugroup-list')
        response = self.client.post(
            url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
