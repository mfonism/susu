from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from ...models import LiveTenure, EsusuGroup
from ...serializers import LiveTenureSerializer


class LiveTenureListAPITest(APITestCase):
    '''
    * User creates a group and becomes admin
    * Admin sets up a future tenure in group

    * Future tenure waiting time elapses and tenure goes live
    * All watches whose users have opted in are converted to live subscriptions
    * At set time, future tenure gets promoted to live tenure
    * User lists live tenures

    GET  /api/live-tenures/
    '''
    def setUp(self):
        mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )

        eg = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=mfon
        )
        LiveTenure.objects.create(amount=10000, esusu_group=eg)

        eg = EsusuGroup.objects.create(
            name='The Financial \'Save-y\'', admin=mfon
        )
        LiveTenure.objects.create(amount=10000, esusu_group=eg)

        self.url = reverse('livetenure-list')

    def test_list_lt(self):
        # ambrose can list all live tenures
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        self.client.force_authenticate(ambrose)

        response = self.client.get(self.url)
        serializer = LiveTenureSerializer(
            LiveTenure.objects.all(),
            many=True,
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_list_lt(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LiveTenureRetrieveAPITest(APITestCase):
    '''
    * User creates a group and becomes admin
    * Admin sets up a future tenure in group
    * At set time, future tenure gets promoted to live tenure
    * User retrieves single live tenures

    GET  /api/live-tenures/<int:pk>/
    '''
    def setUp(self):
        mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )

        eg = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=mfon
        )
        lt = LiveTenure.objects.create(amount=10000, esusu_group=eg)

        self.url = reverse('livetenure-detail', kwargs={'pk': lt.pk})

    def test_retrieve_lt(self):
        # ambrose can retrieve single live tenure
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        self.client.force_authenticate(ambrose)

        response = self.client.get(self.url)
        serializer = LiveTenureSerializer(
            LiveTenure.objects.first(),
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_lt(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
