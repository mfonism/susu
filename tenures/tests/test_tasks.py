from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from hashids import Hashids

from .. import tasks
from ..models import (
    EsusuGroup,
    FutureTenure, LiveTenure,
    Watch, LiveSubscription,
    Contribution
)
from payments.models import Processor


class FutureTenureAndWatchRelatedTasksTest(TestCase):
    '''
    Tests for tasks related to future tenures and watches.

    Especially tasks that have to do with promoting future tenures
    to live tenures,
    and their respective watches to live subscriptions.
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

    def test_pay_dates_are_set_on_resulting_live_tenure(self):
        '''
        When a future tenure is promoted to a live tenure
        previous pay date is set at today
        next pay date is set for 30 days
        '''
        Watch.objects.filter(user=self.mfon).update(status=Watch.OPTED_IN)
        Watch.objects.filter(user=self.watchson).update(status=Watch.OPTED_IN)
        Watch.objects.filter(user=self.watchaholic).update(status=Watch.OPTED_IN)

        tasks.promote_future_tenure(ft_pk=self.ft.pk)

        lt = LiveTenure.objects.get(esusu_group=self.group)

        self.assertEqual(lt.previous_pay_date, (timezone.now()).date())
        self.assertEqual(lt.next_pay_date, (timezone.now() + timezone.timedelta(30)).date())

    def test_increasing_pay_date_is_set_on_resulting_live_subscriptions(self):
        '''
        Resulting live subscriptions have their pay date set on them
        Paydates are set thirty days apart
        With the first live subscription taking on the next pay date of the live tenure.
        '''
        Watch.objects.filter(user=self.mfon).update(status=Watch.OPTED_IN)
        Watch.objects.filter(user=self.watchson).update(status=Watch.OPTED_IN)
        Watch.objects.filter(user=self.watchaholic).update(status=Watch.OPTED_IN)

        tasks.promote_future_tenure(ft_pk=self.ft.pk)

        pay_datetime = timezone.now()
        for lsub in LiveSubscription.objects.filter(tenure__esusu_group=self.group):
            pay_datetime = pay_datetime + timezone.timedelta(30)
            self.assertEqual(lsub.pay_date, pay_datetime.date())


class ContributionsCollectionTasksTest(TestCase):
    '''
    Test the collection of weekly due contributions.

    Contributions are charged to users subscribed whose subscriptions'
    next charge date fall on the day of running the collecting task.

    NOTE: Each subscribing User needs a processor instance
    for all these to happen.
    '''
    def setUp(self):
        # mfon, his group, his lt
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        Processor.objects.create(
            user=self.mfon, card_type=Processor.MASTER_CARD,
            card_id=Hashids(min_length=32).encode(self.mfon.pk),
        )
        group1 = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.mfon
        )
        lt1 = LiveTenure.objects.create(
            amount=5000, esusu_group=group1
        )

        # ambrose, his group, his lt
        ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        Processor.objects.create(
            user=ambrose, card_type=Processor.VERVE,
            card_id=Hashids(min_length=32).encode(ambrose.pk),
        )
        group2 = EsusuGroup.objects.create(
            name='Save for School', admin=ambrose
        )
        lt2 = LiveTenure.objects.create(
            amount=5000, esusu_group=group2
        )

        # the subscribers
        subscriptus = get_user_model().objects.create_user(
            email='watchelina@aol.com', password='iWatchez',
            first_name='Watchelina', last_name='Doe'
        )
        Processor.objects.create(
            user=subscriptus, card_type=Processor.VISA,
            card_id=Hashids(min_length=32).encode(subscriptus.pk),
        )
        subscriptina = get_user_model().objects.create_user(
            email='watchson@gmail.com', password='iAlsoWatcheeze',
            first_name='Watchson', last_name='Johnson'
        )
        Processor.objects.create(
            user=subscriptina, card_type=Processor.INTERSWITCH,
            card_id=Hashids(min_length=32).encode(subscriptina.pk),
        )

        # the subscriptions on mfon's group's lt
        # to be charged today
        LiveSubscription.objects.create(tenure=lt1, user=self.mfon, next_charge_at=timezone.now())
        LiveSubscription.objects.create(tenure=lt1, user=subscriptus, next_charge_at=timezone.now())
        LiveSubscription.objects.create(tenure=lt1, user=subscriptina, next_charge_at=timezone.now())

        # the subscriptions on ambrose's group's lt
        # to be charged in seven days
        LiveSubscription.objects.create(tenure=lt2, user=ambrose)
        LiveSubscription.objects.create(tenure=lt2, user=self.mfon)

    def test_collect_due_contributions(self):
        '''
        Three live subscriptions are due for collection today.
        Three contribution ojects are created after collection.
        '''
        self.assertEqual(Contribution.objects.count(), 0)

        tasks.collect_due_contributions()

        self.assertEqual(Contribution.objects.count(), 3)

    def test_contributions_are_created_only_for_due_subscriptions(self):
        mfons_lt = LiveTenure.objects.get(esusu_group__admin=self.mfon)

        tasks.collect_due_contributions()

        for contribution in Contribution.objects.all():
            self.assertEqual(contribution.tenure, mfons_lt)
