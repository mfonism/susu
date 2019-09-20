import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory

from ...models import FutureTenure, EsusuGroup
from ...serializers import FutureTenureSerializer


class FutureTenureCreateAPITest(APITestCase):
    '''
    User creates a group and becomes admin
    Admin sets up a future tenure in group

    POST  /api/groups/<int:pk>/future-tenure/
    '''
    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.mfon
        )
        self.url = reverse('esusugroup-futuretenure', kwargs={'pk': self.group.pk})
        self.valid_payload = {'amount': 10000}

    def test_create_ft(self):
        '''
        Mfon can create an ft on his group.
        '''
        self.client.force_authenticate(self.mfon)
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        serializer = FutureTenureSerializer(
            FutureTenure.objects.first(),
            context={'request': APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_create_ft(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_create_ft_with_invalid_data(self):
        '''
        Mfon must supply an amount in order to create an ft.
        '''
        self.client.force_authenticate(self.mfon)
        response = self.client.post(
            self.url,
            data=json.dumps({'amount': ''}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_ft_on_someone_elses_group(self):
        '''
        Ambrose is not permitted to create ft in Mfon's own group.
        '''
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


class FutureTenureListAPITest(APITestCase):
    '''
    User creates a group and becomes admin
    Admin sets up a future tenure in group
    Repeat a number of times.

    User lists all future tenures available in app,
    to find out which to watch/join.

    GET  /api/future-tenures/
    '''
    def setUp(self):
        mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        mfons_group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=mfon
        )
        FutureTenure.objects.create(amount=5000, esusu_group=mfons_group)

        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        ag1 = EsusuGroup.objects.create(
            name='Save for School', admin=ambrose
        )
        ag2 = EsusuGroup.objects.create(
            name='Personal Project Savings', admin=ambrose
        )
        FutureTenure.objects.create(amount=5000, esusu_group=ag1)
        FutureTenure.objects.create(amount=5000, esusu_group=ag2)

        self.url = reverse('futuretenure-list')

    def test_list_ft(self):
        '''
        Bryan can list ft's created by Mfon, Ambrose, and any other admin.
        '''
        bryan = get_user_model().objects.create_user(
            email='bryan@stclaire.com', password='passwordless',
            first_name='Bryan', last_name='StClaire'
        )
        self.client.force_authenticate(bryan)

        response = self.client.get(self.url)
        serializer = FutureTenureSerializer(
            FutureTenure.objects.all(),
            many=True,
            context={'request': APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_list_ft(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FutureTenureRetrieveAPITest(APITestCase):
    '''
    User creates a group and becomes admin
    Admin sets up a future tenure in group
    Repeat a number of times.

    User retrieves a single future tenure to possibly place a watch on it.

    GET  /api/future-tenures/<hash_id:pk>/
    '''
    def setUp(self):
        mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=mfon
        )
        ft = FutureTenure.objects.create(amount=5000, esusu_group=group)

        self.url = reverse('futuretenure-detail', kwargs={'pk': ft.pk})

    def test_retrieve_ft(self):
        '''
        Ambrose can retrieve Future Tenure on Mfon's group.
        '''
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        self.client.force_authenticate(ambrose)

        response = self.client.get(self.url)
        serializer = FutureTenureSerializer(
            FutureTenure.objects.first(),
            context={'request':APIRequestFactory().get(self.url)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_unauthenticated_user_cannot_retrieve_ft(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FutureTenureUpdateAPITest(APITestCase):
    '''
    User creates a group and becomes admin
    Admin sets up a future tenure in group
    Admin updates future tenure from group

    PUT  /api/groups/<int:pk>/future-tenure/
    '''
    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.mfon
        )
        ft = FutureTenure.objects.create(amount=5000, esusu_group=group)

        self.url = reverse('esusugroup-futuretenure', kwargs={'pk': group.pk})
        self.valid_payload = {
            'amount': 10000,
            'will_go_live_at': str(timezone.now() + timezone.timedelta(7))
        }

    def test_update_ft(self):
        '''
        Mfon can make an update on the ft in his own group.
        '''
        self.client.force_authenticate(self.mfon)
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

    def test_unauthenticated_user_cannot_update_ft(self):
        response = self.client.put(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_update_ft_in_someone_elses_own_group(self):
        '''
        Ambrose cannot update ft in Mfon's group.
        '''
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
        '''
        Amount must be present in the payload for successful update.
        '''
        self.client.force_authenticate(self.mfon)
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
        '''
        Admin cannot update ft in a group which has no ft, in the first place.
        '''
        self.client.force_authenticate(self.mfon)
        group = EsusuGroup.objects.create(name='Another Group by Mfon', admin=self.mfon)
        url = reverse('esusugroup-futuretenure', kwargs={'pk': group.pk})

        response = self.client.put(
            url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FutureTenureDeleteAPITest(APITestCase):
    '''
    User creates a group and becomes admin
    Admin sets up a future tenure in group
    Admin deletes future tenure from group

    DELETE  /api/groups/<int:pk>/future-tenure/
    '''
    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        group = EsusuGroup.objects.create(
            name='Livelong Savers', admin=self.mfon
        )
        ft = FutureTenure.objects.create(amount=5000, esusu_group=group)

        self.url = reverse('esusugroup-futuretenure', kwargs={'pk':group.pk})

    def test_delete_ft(self):
        '''
        Mfon can delete ft from his group.
        '''
        self.client.force_authenticate(self.mfon)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_user_cannot_delete_ft(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_ft_is_not_soft(self):
        '''
        Assert that DELETE performs a hard delete on the respective ft.
        '''
        eg = EsusuGroup.objects.create(name='To Be Deleted', admin=self.mfon)
        ft = FutureTenure.objects.create(amount=10000, esusu_group=eg)
        self.assertEqual(FutureTenure.objects.count(), 2)

        self.client.force_authenticate(self.mfon)
        url = reverse('esusugroup-futuretenure', kwargs={'pk':eg.pk})
        self.client.delete(self.url)

        self.assertEqual(FutureTenure.objects.count(), 1)
        self.assertEqual(FutureTenure.all_objects.count(), 1)

    def test_cannot_delete_ft_on_someone_elses_own_group(self):
        '''
        Ambrose cannot delete ft from group where Mfon is admin.
        '''
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
