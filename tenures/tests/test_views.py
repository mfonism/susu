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


class EsusuGroupDetailApiTest(APITestCase):

    def setUp(self):
        self.user1 = get_user_model().objects.create(
            email='itoro@etimfon.com', password='nopassword'
        )
        self.group1 = EsusuGroup.objects.create(
            name='Aity\'s Group', admin=self.user1
        )

        self.user2 = get_user_model().objects.create(
            email='mfon@etimfon.com', password='4g8menut!'
        )
        self.group2 = EsusuGroup.objects.create(
            name='Mfonism\'s Group', admin=self.user2
        )

    def test_retrieve_group(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('esusugroup-detail', kwargs={'pk': self.group2.pk})
        response = self.client.get(url)

        serializer = EsusuGroupSerializer(
            EsusuGroup.objects.get(pk=self.group2.pk),
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_group(self):
        url = reverse('esusugroup-detail', kwargs={'pk': self.group2.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EsusuGroupUpdateApiTest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            email='mfon@etimfon', password='4g8menut!'
        )
        self.group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.user
        )

    def test_update_group(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-detail', kwargs={'pk':self.group.pk})

        data = self.client.get(url).data
        serializer = EsusuGroupSerializer(
            self.group,
            context={'request': APIRequestFactory().get(url)}
        )
        self.assertEqual(data, serializer.data)

        new_name = 'Lifelong Savers in Nigeria'
        data['name'] = new_name
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.group.refresh_from_db()
        self.assertEqual(self.group.name, new_name)

        serializer = EsusuGroupSerializer(
            self.group,
            context={'request': APIRequestFactory().get(url)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_cannot_update_group_with_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-detail', kwargs={'pk':self.group.pk})
        response = self.client.put(
            url,
            data=json.dumps({'foo':'bar'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_update_group(self):
        url = reverse('esusugroup-detail', kwargs={'pk':self.group.pk})
        response = self.client.put(
            url,
            data=json.dumps({'foo':'bar'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
