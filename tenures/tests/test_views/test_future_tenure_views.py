from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from ...models import FutureTenure, EsusuGroup
from ...serializers import FutureTenureSerializer


def _create_fts(obj, user, group_names=None):
    '''
    create groups with given group names for given user, 
    create future tenures for these groups,
    '''
    if not group_names:
        return
    for name in group_names:
        eg = EsusuGroup.objects.create(name=name, admin=user)
        FutureTenure.objects.create(amount=10000, esusu_group=eg)


class FutureTenureListAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.url = reverse('futuretenure-list')

    def test_list_ft(self):
        # authenticated user can list future tenures
        self.client.force_authenticate(self.user)
        _create_fts(
            self,
            self.user,
            ('Lifelong Savers', 'The Financial \'Save-y\'')
        )

        response = self.client.get(self.url)
        serializer = FutureTenureSerializer(
            FutureTenure.objects.all(),
            many=True,
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_list_ft(self):
        _create_fts(
            self,
            self.user,
            ('Lifelong Savers', 'The Financial \'Save-y\'')
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FutureTenureRetrieveAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        eg = EsusuGroup.objects.create(name='Lifelong Savers', admin=self.user)
        ft = FutureTenure.objects.create(amount=5000, esusu_group=eg)

        self.url = reverse('futuretenure-detail', kwargs={'pk': ft.pk})

    def test_retrieve_ft(self):
        # authenticated user can retrieve future tenure
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url)
        serializer = FutureTenureSerializer(
            FutureTenure.objects.first(),
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_ft(self):
        # unauthenticated user is not authorized to retrieve future tenure
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
