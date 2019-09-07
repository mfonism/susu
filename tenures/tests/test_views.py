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
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!'
        )
        EsusuGroup.objects.create(name='First Group', admin=self.user)
        EsusuGroup.objects.create(name='Second Group', admin=self.user)
        EsusuGroup.objects.create(name='Third Group', admin=self.user)
        EsusuGroup.objects.create(name='Fourth Group', admin=self.user)

    def test_list_group(self):
        # authenticated user can retrieve list of groups
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
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!'
        )
        self.valid_payload = {
            'name': 'Lifelong Savers',
        }

    def test_create_group(self):
        # authenticated user can create group
        # ...automatically becomes group admin, too
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-list')
        response = self.client.post(
            url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        esusugroup = EsusuGroup.objects.get(pk=response.data['pk'])
        serializer = EsusuGroupSerializer(
            esusugroup,
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(esusugroup.admin.pk, self.user.pk)

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
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!'
        )
        self.group = EsusuGroup.objects.create(
            name='Mfonism\'s Group', admin=self.user
        )

    def test_retrieve_group(self):
        # authenticated user can retrieve own group
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-detail', kwargs={'pk': self.group.pk})
        response = self.client.get(url)

        serializer = EsusuGroupSerializer(
            EsusuGroup.objects.get(pk=self.group.pk),
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_non_owner_can_retrieve_group(self):
        # authenticated user can retrieve group owned by some other user
        ambrose = get_user_model().objects.create_user(
            'ambrose@igibo.com', 'nopassword'
            )
        self.client.force_authenticate(user=ambrose)
        url = reverse('esusugroup-detail', kwargs={'pk': self.group.pk})
        response = self.client.get(url)

        serializer = EsusuGroupSerializer(
            EsusuGroup.objects.get(pk=self.group.pk),
            context={'request': APIRequestFactory().get(url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_group(self):
        url = reverse('esusugroup-detail', kwargs={'pk': self.group.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EsusuGroupUpdateApiTest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon', password='4g8menut!'
        )
        self.group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.user
        )

    def test_update_group(self):
        # authenticated user can update own group
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-detail', kwargs={'pk':self.group.pk})

        new_name = 'Group Of Analytical Thinkers (G.O.A.T)'
        response = self.client.put(
            url,
            data=json.dumps({'name': new_name}),
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

    def test_can_only_update_own_group(self):
        # a user cannot update a group whose admin they are not
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword'
        )
        group_of_life = EsusuGroup.objects.create(
            name='The Group of Life', admin=ambrose
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-detail', kwargs={'pk':group_of_life.pk})
        response = self.client.put(
            url,
            data=json.dumps({'name': 'Change!'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EsusuGroupDeleteApiTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8m4nut!'
        )
        self.group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.user
        )

    def test_delete_group(self):
        # authenticated user can delete own group
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-detail', kwargs={'pk':self.group.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_is_soft(self):
        # delete merely sets a flag on the object
        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-detail', kwargs={'pk':self.group.pk})
        response = self.client.delete(url)

        self.assertFalse(EsusuGroup.objects.filter(pk=self.group.pk).exists())
        self.assertTrue(EsusuGroup.all_objects.filter(pk=self.group.pk).exists())

    def test_can_only_delete_own_group(self):
        # authenticated user can only delete own group
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword'
        )
        group_of_life = EsusuGroup.objects.create(
            name='The Group of Life', admin=ambrose
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('esusugroup-detail', kwargs={'pk':group_of_life.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_group(self):
        url = reverse('esusugroup-detail', kwargs={'pk':self.group.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
