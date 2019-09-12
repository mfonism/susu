import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse

from ...views import EsusuGroupViewSet
from ...models import (
    EsusuGroup,
    FutureTenure, HistoricalTenure
)
from ...serializers import (
    EsusuGroupSerializer,
    FutureTenureSerializer, HistoricalTenureSerializer
)


class EsusuGroupListApiTest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
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
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
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

        esusugroup = EsusuGroup.objects.get(pk=1)
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
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
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
            'ambrose@igibo.com', 'nopassword',
            first_name='Ambrose', last_name='Igibo'
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
            email='mfon@etimfon', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
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
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
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
            email='mfon@etimfon.com', password='4g8m4nut!',
            first_name='Mfon', last_name='Eti-mfon'
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
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
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


class FutureTenureCreateAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.group = EsusuGroup.objects.create(name='Livelong Savers', admin=self.user)

        self.url = reverse('esusugroup-futuretenure', kwargs={'pk':self.group.pk})
        self.valid_payload = {
            'amount': 10000,
        }

    def test_create_ft(self):
        # authenticated user can create future tenure
        # in a group they own
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        serializer = FutureTenureSerializer(
            FutureTenure.objects.first(),
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_cannot_create_ft_with_invalid_data(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_only_create_ft_in_own_group(self):
        # authenticated user cannot create
        # future tenure in someone else's group
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        self.client.force_authenticate(ambrose)

        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create_ft(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FutureTenureUpdateAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        eg = EsusuGroup.objects.create(name='Livelong Savers', admin=self.user)
        ft = FutureTenure.objects.create(amount=5000, esusu_group=eg)

        self.url = reverse('esusugroup-futuretenure', kwargs={'pk':eg.pk})
        self.valid_payload = {
            'amount': 10000,
            'will_go_live_at': str(timezone.now() + timezone.timedelta(7))
        }

    def test_update_ft(self):
        # authenticated user can update future tenure
        # in a group they own
        self.client.force_authenticate(self.user)
        response = self.client.put(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        serializer = FutureTenureSerializer(
            FutureTenure.objects.first(),
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_can_only_update_ft_in_own_group(self):
        # authenticated user can only update future tenure
        # in their own group
        ambrose = get_user_model().objects.create_user(
            'ambrose@igibo.com', 'nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        self.client.force_authenticate(ambrose)

        response = self.client.put(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_ft_with_invalid_data(self):
        # authenticated user can only update future tenure
        # with valid data
        self.client.force_authenticate(self.user)
        invalid_data = {
            'will_go_live_at': str(timezone.now() + timezone.timedelta(7))
        }

        response = self.client.put(
            self.url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_update_non_existent_ft(self):
        # authenticated user cannot update future tenure
        # in a group that has no future tenure in the first place
        self.client.force_authenticate(self.user)
        eg = EsusuGroup.objects.create(name='Another Group by Mfon', admin=self.user)
        url = reverse('esusugroup-futuretenure', kwargs={'pk':eg.pk})

        response = self.client.put(
            url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_update_ft(self):
        response = self.client.put(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FutureTenureDeleteAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        eg = EsusuGroup.objects.create(name='Livelong Savers', admin=self.user)
        ft = FutureTenure.objects.create(amount=5000, esusu_group=eg)

        self.url = reverse('esusugroup-futuretenure', kwargs={'pk':eg.pk})

    def test_delete_ft(self):
        # authenticated user can delete future tenure from
        # their own group
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_ft_is_not_soft(self):
        eg = EsusuGroup.objects.create(name='To Be Deleted', admin=self.user)
        ft = FutureTenure.objects.create(amount=10000, esusu_group=eg)
        self.assertEqual(FutureTenure.objects.count(), 2)

        self.client.force_authenticate(self.user)
        url = reverse('esusugroup-futuretenure', kwargs={'pk':eg.pk})
        self.client.delete(self.url)

        self.assertEqual(FutureTenure.objects.count(), 1)
        self.assertEqual(FutureTenure.all_objects.count(), 1)

    def test_can_only_delete_own_ft(self):
        # authenticated user cannot delete future tenure from
        # group not owned by them
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        eg = EsusuGroup.objects.create(name='To Be Deleted', admin=ambrose)
        ft = FutureTenure.objects.create(amount=10000, esusu_group=eg)

        self.client.force_authenticate(ambrose)
        # can ambrose delete mfon's future tenure?
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_ft(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HistoricalTenureListAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        eg = EsusuGroup.objects.create(name='Lifelong Savers', admin=self.user)
        # lasted a year
        HistoricalTenure.objects.create(
            amount=10000, esusu_group=eg,
            live_at=timezone.now() - timezone.timedelta(365)
        )
        # a year minus july and august
        HistoricalTenure.objects.create(
            amount=5000, esusu_group=eg,
            live_at=timezone.now() - timezone.timedelta(303)
        )
        # a year and two months (july and august occuring twice, each)
        HistoricalTenure.objects.create(
            amount=20000, esusu_group=eg,
            live_at=timezone.now() - timezone.timedelta(427)
        )
        self.url = reverse('esusugroup-historicaltenure', kwargs={'pk': eg.pk})

    def test_list_ht(self):
        # authenticated user can list historical tenure
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)

        serializer = HistoricalTenureSerializer(
            HistoricalTenure.objects.all(),
            many=True,
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def unauthenticated_user_cannot_list_ht(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
