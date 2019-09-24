from django.contrib.auth import get_user_model
from django.test import TestCase

from .. import tasks
from ..models import (
    EsusuGroup,
    FutureTenure, LiveTenure,
    Watch, LiveSubscription
)


class TasksTest(TestCase):

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

    def test_reset_watches_on_updated_future_tenure(self):
        for w in Watch.objects.filter(tenure=self.ft):
            self.assertEqual(w.status, Watch.JUST_WATCHING)

        tasks.reset_watches_on_updated_future_tenure(ft_pk=self.ft.pk)

        for watch in Watch.objects.all():
            self.assertEqual(watch.status, Watch.TO_REVIEW_UPDATE)

    def test_promote_future_tenure(self):
        # before promotion: 1 ft, 0 lt
        self.assertEqual(FutureTenure.objects.filter(pk=self.ft.pk).count(), 1)
        self.assertEqual(LiveTenure.objects.filter(esusu_group=self.group).count(), 0)
        self.assertEqual(LiveTenure.all_objects.filter(esusu_group=self.group).count(), 0)

        tasks.promote_future_tenure(ft_pk=self.ft.pk)

        # after promotion: 0 ft, 1 lt
        self.assertEqual(FutureTenure.objects.filter(pk=self.ft.pk).count(), 0)
        self.assertEqual(FutureTenure.all_objects.filter(pk=self.ft.pk).count(), 0)
        self.assertEqual(LiveTenure.objects.filter(esusu_group=self.group).count(), 1)

    def test_promote_future_tenure_promotes_all_opted_in_watches(self):
        Watch.objects.filter(user=self.mfon).update(status=Watch.OPTED_IN)
        Watch.objects.filter(user=self.watchson).update(status=Watch.OPTED_IN)
        Watch.objects.filter(user=self.watchaholic).update(status=Watch.OPTED_IN)

        tasks.promote_future_tenure(ft_pk=self.ft.pk)

        self.assertEqual(LiveSubscription.objects.filter(tenure__esusu_group=self.group).count(), 3)

    def test_opted_in_watches_are_promoted_in_random_order(self):
        '''
        Live subscriptions on a live tenure are created in a random order,
        compared to the ordering of their respective watches.
        '''
        Watch.objects.update(status=Watch.OPTED_IN)

        # users in the order with which their watches were created
        users = list(watch.user for watch in Watch.objects.filter(tenure=self.ft, status=Watch.OPTED_IN))

        tasks.promote_future_tenure(ft_pk=self.ft.pk)

        # users in the (RANDOM) order with which their live subscriptions were created
        users_ls = list(sub.user for sub in LiveSubscription.objects.filter(tenure__esusu_group=self.group))

        self.assertCountEqual(users, users_ls)
        self.assertNotEqual(users, users_ls)
        self.assertEqual(len(users), len(users_ls))

    def test_promote_future_tenure_deletes_all_watches(self):
        # before promotion: 4 watches
        self.assertEqual(Watch.objects.filter(tenure=self.ft).count(), 4)

        tasks.promote_future_tenure(ft_pk=self.ft.pk)

        # after promotion: 0 watches
        self.assertEqual(Watch.objects.filter(tenure=self.ft).count(), 0)
        self.assertEqual(Watch.all_objects.filter(tenure=self.ft).count(), 0)
