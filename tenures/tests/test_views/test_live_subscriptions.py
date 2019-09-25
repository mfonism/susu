from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from ...models import EsusuGroup, LiveTenure, LiveSubscription
from ...serializers import LiveSubscriptionSerializer


class LiveSubscriptionListAPITest(APITestCase):
    '''
    * User creates esusu group and becomes group admin
    * Group admin creates future tenure on esusu group
    * User creates watch on future tenure to opt in or out

    * Future tenure waiting time elapses and tenure goes live
    * All watches whose users have opted in are converted to live subscriptions

    * Group admin lists live subscriptions on group

    GET  /api/groups/<int:pk>/live-subscription/
    '''
    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.mfon
        )
        self.lt = LiveTenure.objects.create(
            amount=5000, esusu_group=self.group
        )

        # the subscribers
        self.subscriptus = get_user_model().objects.create_user(
            email='watchelina@aol.com', password='iWatchez',
            first_name='Watchelina', last_name='Doe'
        )
        self.subscriptina = get_user_model().objects.create_user(
            email='watchson@gmail.com', password='iAlsoWatcheeze',
            first_name='Watchson', last_name='Johnson'
        )

        # the subscriptions
        LiveSubscription.objects.create(
            tenure=self.lt, user=self.mfon
        )
        LiveSubscription.objects.create(
            tenure=self.lt, user=self.subscriptus
        )
        LiveSubscription.objects.create(
            tenure=self.lt, user=self.subscriptina
        )

        self.url = reverse('esusugroup-livesubscription', kwargs={'pk': self.group.pk})

    def test_list_ls(self):
        # Mfon can list subscriptions on his own group
        self.client.force_authenticate(self.mfon)

        response = self.client.get(self.url)
        serializer = LiveSubscriptionSerializer(
            LiveSubscription.objects.filter(tenure=self.lt),
            many=True,
            context={'request': APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_list_subscriptions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_list_subscriptions_on_someone_elses_group(self):
        # no one but Mfon can list subscriptions on Mfon's own group
        self.client.force_authenticate(self.subscriptina)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LiveSubscriptionRetrieveAPITest(APITestCase):
    '''
    * User creates esusu group and becomes group admin
    * Group admin creates future tenure on esusu group
    * User creates watch on future tenure to opt in or out

    * Future tenure waiting time elapses and tenure goes live
    * All watches whose users have opted in are converted to live subscriptions

    * User retrieves their own live subscription

    GET  /api/live-subscriptions/<int:pk>/
    '''
    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.mfon
        )
        lt = LiveTenure.objects.create(
            amount=5000, esusu_group=group
        )

        # the subscribers
        self.subscriptus = get_user_model().objects.create_user(
            email='watchelina@aol.com', password='iWatchez',
            first_name='Watchelina', last_name='Doe'
        )
        self.subscriptina = get_user_model().objects.create_user(
            email='watchson@gmail.com', password='iAlsoWatcheeze',
            first_name='Watchson', last_name='Johnson'
        )

        # the subscriptions
        LiveSubscription.objects.create(
            tenure=lt, user=self.mfon
        )
        LiveSubscription.objects.create(
            tenure=lt, user=self.subscriptus
        )
        self.ls = LiveSubscription.objects.create(
            tenure=lt, user=self.subscriptina
        )

        self.url = reverse('livesubscription-detail', kwargs={'pk': self.ls.pk})

    def test_retrieve_ls(self):
        # Subscriptina can list his live subscription
        self.client.force_authenticate(self.subscriptina)

        response = self.client.get(self.url)
        serializer = LiveSubscriptionSerializer(
            self.ls,
            context={'request': APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_ls(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_retrieve_someone_elses_ls(self):
        # Mfon cannot retrieve subscriptina's live subscription
        self.client.force_authenticate(self.mfon)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
