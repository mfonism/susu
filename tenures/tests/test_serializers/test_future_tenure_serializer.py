from django.contrib.auth import get_user_model
from django.utils import timezone
# from django_dramatiq.test import DramatiqTestCase
from rest_framework.test import APITestCase, APIRequestFactory #, APIClient
from rest_framework.reverse import reverse

from ... import tasks
from ...models import EsusuGroup, FutureTenure, Watch
from ...serializers import FutureTenureSerializer


class FutureTenureSerializerCreateTest(APITestCase):
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
        Default live time is 14 days.
        '''
        serializer = FutureTenureSerializer(
            data=self.valid_payload,
            context={'request': APIRequestFactory().get(self.url)}
        )

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(esusu_group=self.group)
        
        self.assertEqual(
            instance.will_go_live_at.date(),
            (timezone.now() + timezone.timedelta(14)).date()
        )

    def test_create_ft_with_short_live_time(self):
        '''
        If live time is supplied in data dict, and is less than 2 days,
        it is ignored, and 2 days is set.
        '''
        serializer = FutureTenureSerializer(
            data={
                'amount': 5000,
                'will_go_live_at': str(timezone.now() + timezone.timedelta(1))
            },
            context={
                'request': APIRequestFactory().get(self.url)
            }
        )

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(esusu_group=self.group)
        
        self.assertEqual(
            instance.will_go_live_at.date(),
            (timezone.now() + timezone.timedelta(2)).date()
            )

    def test_create_ft_with_fair_live_time(self):
        '''
        If live time is supplied in data dict, and is more than 2 days,
        it is left as is.
        '''
        serializer = FutureTenureSerializer(
            data={
                'amount': 5000,
                'will_go_live_at': str(timezone.now() + timezone.timedelta(3))
            },
            context={
                'request': APIRequestFactory().get(self.url)
            }
        )

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(esusu_group=self.group)
        
        self.assertEqual(
            instance.will_go_live_at.date(),
            (timezone.now() + timezone.timedelta(3)).date()
        )


# class FutureTenureSerializerUpdateTest(DramatiqTestCase):
#    client_class = APIClient    # so that we can call self.client
class FutureTenureSerializerUpdateTest(APITestCase):

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

        # the watchers
        self.watchelina = get_user_model().objects.create_user(
            email='watchelina@aol.com', password='iWatchez',
        
            first_name='Watchelina', last_name='Doe'
        )
        self.watchson = get_user_model().objects.create_user(
            email='watchson@gmail.com', password='iAlsoWatcheeze',
            first_name='Watchson', last_name='Johnson'
        )
        self.watchaholic = get_user_model().objects.create_user(
            email='watchaholic@aim.com', password='iWatchalot',
            first_name='Watchaholic', last_name='Trump'
        )

        # watches
        Watch.objects.create(
            user=self.mfon, tenure=self.ft
        )
        Watch.objects.create(
            user=self.watchelina, tenure=self.ft
        )
        Watch.objects.create(
            user=self.watchson, tenure=self.ft
        )
        Watch.objects.create(
            user=self.watchaholic, tenure=self.ft
        )

        self.url = reverse('esusugroup-futuretenure', kwargs={'pk': self.group.pk})
        self.valid_payload = {'amount': 10000}

    def test_updating_ft_resets_status_on_watches(self):
        serializer = FutureTenureSerializer(
            self.ft,
            data=self.valid_payload,
            context={'request': APIRequestFactory().get(self.url)}
        )

        for watch in Watch.objects.all():
            self.assertEqual(watch.status, Watch.JUST_WATCHING)

        self.assertTrue(serializer.is_valid())
        instance = serializer.save()

        # wait for all the tasks to be processed
        # self.broker.join(tasks.reset_watches_on_updated_future_tenure.queue_name)
        # self.worker.join()

        for watch in Watch.objects.all():
            self.assertEqual(watch.status, Watch.TO_REVIEW_UPDATE)

    def test_update_ft_with_short_live_time(self):
        '''
        If live time is supplied in data dict, and is less than 2 days,
        it is ignored, and 2 days is set.
        '''
        serializer = FutureTenureSerializer(
            self.ft,
            data={
                'amount': 5000,
                'will_go_live_at': str(timezone.now() + timezone.timedelta(1))
            },
            context={
                'request': APIRequestFactory().get(self.url)
            }
        )

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(esusu_group=self.group)
        
        self.assertEqual(
            instance.will_go_live_at.date(),
            (timezone.now() + timezone.timedelta(2)).date()
        )

    def test_create_ft_with_fair_live_time(self):
        '''
        If live time is supplied in data dict, and is more than 2 days,
        it is left as is.
        '''
        serializer = FutureTenureSerializer(
            self.ft,
            data={
                'amount': 5000,
                'will_go_live_at': str(timezone.now() + timezone.timedelta(3))
            },
            context={
                'request': APIRequestFactory().get(self.url)
            }
        )

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(esusu_group=self.group)
        
        self.assertEqual(
            instance.will_go_live_at.date(),
            (timezone.now() + timezone.timedelta(3)).date()
        )
