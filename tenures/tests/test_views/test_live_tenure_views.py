from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from ...models import LiveTenure, EsusuGroup
from ...serializers import LiveTenureSerializer


def _create_lts(obj, user, group_names=None):
    '''
    create groups with given group names for given user, 
    create live tenures for these groups,
    '''
    if not group_names:
        return
    for name in group_names:
        eg = EsusuGroup.objects.create(name=name, admin=user)
        LiveTenure.objects.create(amount=10000, esusu_group=eg)


class LiveTenureListAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.url = reverse('livetenure-list')

    def test_list_lt(self):
        # authenticated user can list live tenures
        self.client.force_authenticate(self.user)
        _create_lts(
            self,
            self.user,
            ('Lifelong Savers', 'The Financial \'Save-y\'')
        )

        response = self.client.get(self.url)
        serializer = LiveTenureSerializer(
            LiveTenure.objects.all(),
            many=True,
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_list_lt(self):
        _create_lts(
            self,
            self.user,
            ('Lifelong Savers', 'The Financial \'Save-y\'')
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LiveTenureRetrieveAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        eg = EsusuGroup.objects.create(name='Lifelong Savers', admin=self.user)
        lt = LiveTenure.objects.create(amount=5000, esusu_group=eg)

        self.url = reverse('livetenure-detail', kwargs={'pk': lt.pk})

    def test_retrieve_lt(self):
        # authenticated user can retrieve live tenure
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url)
        serializer = LiveTenureSerializer(
            LiveTenure.objects.first(),
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_lt(self):
        # unauthenticated user is not authorized to retrieve live tenure
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
