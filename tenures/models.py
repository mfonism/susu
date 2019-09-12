from django.db import models
from django.conf import settings
from django.utils import timezone
from hashids import Hashids

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
        return whether the argument user is a member of the group.
        '''
        # for now
        return True


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
    esusu_group = models.OneToOneField(EsusuGroup, on_delete=models.CASCADE)
    live_at = models.DateTimeField(auto_now_add=True)

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


def two_weeks_from_now():
    return timezone.now() + timezone.timedelta(14)


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
    esusu_group = models.OneToOneField(EsusuGroup, on_delete=models.CASCADE)
    will_go_live_at = models.DateTimeField(default=two_weeks_from_now)

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
    has_opted_in = models.BooleanField(
        default=False,
        help_text='Indicates whether the user has opted to join the watched tenure when it eventually goes live'
    )

    class Meta:
        ordering = ['-created_at']
