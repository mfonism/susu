from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from hashids import Hashids

from . import utils
from shrewd_models.models import AbstractShrewdModelMixin


hasher = Hashids(min_length=11)

class EsusuGroup(AbstractShrewdModelMixin, models.Model):
    name = models.CharField(max_length=64)
    hash_id = models.CharField(max_length=64, editable=False)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+'
    )

    class Meta:
        ordering = ['-created_at']

    @staticmethod
    def get_hash_id(pk):
        '''
        return a unique hash built from the passed product key.
        '''
        return hasher.encode(pk)

    def __str__(self):
        return self.name or self.hash_id or str(self.pk)

    def has_member(self, user):
        '''
        Return whether the argument user is a member of the group.

        A user is a member of a group if they are either watching a future
        tenure on the group, or are subscribed to a live tenure on it.
        '''
        return (user == self.admin
            or self.has_watching_member(user)
            or self.has_live_member(user)
        )

    def has_watching_member(self, user):
        try:
            return user in self.future_tenure.watchers.all()
        except ObjectDoesNotExist:
            return False

    def has_live_member(self, user):
        try:
            return user in self.live_tenure.subscribers.all()
        except ObjectDoesNotExist:
            return False


class LiveTenure(AbstractShrewdModelMixin, models.Model):
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        help_text='The amount of money to be saved each week per subscriber.',
        editable=False
    )
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='LiveSubscription',
        through_fields=('tenure', 'user'),
        related_name='+'
    )
    esusu_group = models.OneToOneField(
        EsusuGroup,
        on_delete=models.CASCADE,
        related_name='live_tenure'
    )
    live_at = models.DateTimeField(auto_now_add=True)
    previous_pay_date = models.DateField(null=True)
    next_pay_date = models.DateField(null=True)

    class Meta:
        ordering = ['-live_at', '-created_at']


class HistoricalTenure(AbstractShrewdModelMixin, models.Model):
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        help_text='The amount of money that was saved each week per subscriber.'
    )
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='HistoricalSubscription',
        through_fields=('tenure', 'user'),
        related_name='+'
    )
    esusu_group = models.ForeignKey(
        EsusuGroup,
        on_delete=models.CASCADE,
        related_name='historical_tenures'
    )
    live_at = models.DateTimeField()

    class Meta:
        ordering = ['-live_at']


class FutureTenure(AbstractShrewdModelMixin, models.Model):
    # the hash_id will be passed from the group to the tenure
    hash_id = models.CharField(
        primary_key=True,
        max_length=64,
        unique=True
    )
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        help_text='The amount of money to be saved each week per subscriber.'
    )
    watchers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Watch',
        through_fields=('tenure', 'user'),
        related_name='+'
    )
    esusu_group = models.OneToOneField(
        EsusuGroup,
        on_delete=models.CASCADE,
        related_name='future_tenure'
    )
    will_go_live_at = models.DateTimeField(default=utils.two_weeks_from_now)

    class Meta:
        ordering = ['-will_go_live_at', '-created_at']

    def get_hash_id(self):
        return self.esusu_group.hash_id


class LiveSubscription(AbstractShrewdModelMixin, models.Model):
    '''
    Intermediary model implementing the relationship between 
    users and the tenures they are currently subscribed to.
    '''
    tenure = models.ForeignKey(
        LiveTenure,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+'
    )
    next_charge_at = models.DateTimeField(default=utils.seven_days_from_now)
    pay_date = models.DateField(null=True)

    def reset_next_charge_date(self):
        self.next_charge_at = utils.seven_days_from_now()
        self.save()

    class Meta:
        ordering = ['-created_at']


class HistoricalSubscription(AbstractShrewdModelMixin, models.Model):
    '''
    Intermediary model implementing the relationship between 
    users and the tenures they previously subscribed to.
    '''
    tenure = models.ForeignKey(
        HistoricalTenure,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+'
    )

    class Meta:
        ordering = ['-created_at']


class Watch(AbstractShrewdModelMixin, models.Model):
    '''
    Intermediary model implementing the relationship between 
    users and the future tenures they are keeping their eyes on.
    '''
    OPTED_IN = 'Opted In'
    JUST_WATCHING = 'Just Watching'
    TO_REVIEW_UPDATE = 'To Review Update'

    STATUS_OPTIONS = (
        (JUST_WATCHING, JUST_WATCHING),
        (OPTED_IN, OPTED_IN),
        (TO_REVIEW_UPDATE, TO_REVIEW_UPDATE)
    )

    tenure = models.ForeignKey(
        FutureTenure,
        on_delete=models.CASCADE,
        related_name='watches'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+'
    )
    status = models.CharField(
        blank=True,
        default=JUST_WATCHING,
        max_length=16,
        choices=STATUS_OPTIONS,
        help_text='Indicates whether the user has opted to join the watched tenure when it eventually goes live'
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ['tenure', 'user']


class Contribution(AbstractShrewdModelMixin, models.Model):
    '''
    Model implementing a weekly contribution of an amount to a live tenure.
    '''
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        help_text='The amount of money on this contribution.',
        editable=False
    )
    tenure = models.ForeignKey(
        LiveTenure,
        on_delete=models.PROTECT,
        related_name='contributions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+'
    )
