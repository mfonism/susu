import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from ...models import EsusuGroup, FutureTenure, Watch
from ...serializers import WatchSerializer


class WatchCreateAPITest(APITestCase):
    '''
    User creates a group and becomes admin
    Admin sets up a future tenure in group
    User watches (future tenure in) group to receive updates

    POST  /api/groups/<int:pk>/watch/
    '''
    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.mfon
        )
        self.ft = FutureTenure.objects.create(
            esusu_group=self.group, amount=5000
        )
        self.url = reverse('esusugroup-watch', kwargs={'pk':self.group.pk})

        self.watchelina = get_user_model().objects.create_user(
            email='watchelina@aol.com', password='iWatchez',
            first_name='Watchelina', last_name='Doe'
        )

    def test_create_watch(self):
        self.client.force_authenticate(self.watchelina)
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )

        serializer = WatchSerializer(
            Watch.objects.filter(tenure=self.ft, user=self.watchelina).get(),
            context={'request': APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_create_watch(self):
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_create_watch_on_group_user_is_already_watching(self):
        self.client.force_authenticate(self.watchelina)
        self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )

        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_watch_on_group_with_no_ft(self):
        eg = EsusuGroup.objects.create(
            name='Has no FT!', admin=self.mfon
        )
        eg_url = reverse('esusugroup-watch', kwargs={'pk': eg.pk})

        self.client.force_authenticate(self.watchelina)
        response = self.client.post(
            eg_url,
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WatchListAPITest(APITestCase):
    '''
    User creates a group and becomes admin
    Admin sets up a future tenure in group
    Users watch (future tenure in) group to receive updates
    Admin lists watches on the group

    GET  /api/groups/<int:pk>/watch/
    '''
    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.mfon
        )
        self.ft = FutureTenure.objects.create(
            esusu_group=self.group, amount=5000
        )
        self.url = reverse('esusugroup-watch', kwargs={'pk':self.group.pk})

        # the watchers
        self.watchelina = get_user_model().objects.create_user(
            email='watchelina@aol.com', password='iWatchez',
            first_name='Watchelina', last_name='Doe'
        )
        self.watchson = get_user_model().objects.create_user(
            email='watchson@gmail.com', password='iAlsoWatcheeze',
            first_name='Watchson', last_name='Johnson'
        )

        # in the API, the view should automatically create a watch for
        # group admin on future tenure creation
        Watch.objects.create(
            user=self.mfon, tenure=self.ft
        )

        # the other watches
        Watch.objects.create(
            user=self.watchelina, tenure=self.ft
        )
        Watch.objects.create(
            user=self.watchson, tenure=self.ft
        )

    def test_list_watches(self):
        self.client.force_authenticate(self.mfon)
        response = self.client.get(self.url)

        serializer = WatchSerializer(
            Watch.objects.filter(tenure__esusu_group=self.group),
            many=True,
            context={'request': APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_list_watches(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_list_watches_not_belonging_to_group_identified_by_view(self):
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        eg = EsusuGroup.objects.create(
            name='Save for School', admin=ambrose
        )
        ft = FutureTenure.objects.create(
            esusu_group=eg, amount=20000
        )

        # four watches for ambrose's group
        for user in [ambrose, self.mfon, self.watchelina, self.watchson]:
            Watch.objects.create(
                user=user, tenure=ft
            )

        self.client.force_authenticate(self.mfon)
        response = self.client.get(self.url)

        # only the three watches created in setUp are seen
        self.assertEqual(len(response.data), 3)

    def test_cannot_list_watches_if_not_admin_of_group_identified_by_view(self):
        self.client.force_authenticate(self.watchelina)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
