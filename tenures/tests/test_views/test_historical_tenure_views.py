from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from ...models import HistoricalTenure, EsusuGroup
from ...serializers import HistoricalTenureSerializer


class HistoricalTenureRetrieveAPITest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        eg = EsusuGroup.objects.create(name='Lifelong Savers', admin=self.user)
        ht = HistoricalTenure.objects.create(
            amount=10000, esusu_group=eg,
            live_at=timezone.now() - timezone.timedelta(365)
        )
        self.url = reverse('historicaltenure-detail', kwargs={'pk': ht.pk})

    def test_retrieve_ht(self):
        # authenticated user can retrieve historical tenure
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url)
        serializer = HistoricalTenureSerializer(
            HistoricalTenure.objects.first(),
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_ht(self):
        # unauthenticated user is not authorized to retrieve historical tenure
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
