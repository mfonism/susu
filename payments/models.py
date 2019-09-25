from django.conf import settings
from django.db import models

from shrewd_models.models import AbstractShrewdModelMixin
from .utils import Alert, AlertStatus, AlertType


class Processor(AbstractShrewdModelMixin, models.Model):
    '''
    Model for processing payments.

    Dummy for now.
    '''
    INTERSWITCH = 'Interswitch'
    MASTER_CARD = 'Master Card'
    VERVE = 'Verve'
    VISA = 'Visa'

    CARD_TYPE_OPTIONS = (
        (INTERSWITCH, INTERSWITCH),
        (MASTER_CARD, MASTER_CARD),
        (VERVE, VERVE),
        (VISA, VISA)
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+'
    )
    card_type = models.CharField(
        max_length=16,
        choices=CARD_TYPE_OPTIONS,
    )
    card_id = models.CharField(
        max_length=128,
        help_text='The ID supplied by the card provider (issuing financial institution) on owner verification'
    )

    def charge(self, amount):
        '''
        Charge the argument amount on the card.

        For now just return a successful alert.
        '''
        # this is where we'll make an appropriate request to card provider
        # if the request is successful
        # we'll probably save the money to our company's escrow
        # regardless, we'll return an appropriate alert as response
        return Alert.make_charge_alert(self.user.pk, amount)

    def credit(self, amount):
        '''
        Credit the argument amount to the card.

        For now just return a successful alert.
        '''
        # this is where we'll make an appropriate request to card provider
        # we'll probably move the money from our company's escrow
        # then return an appropriate alert as response
        return Alert.make_credit_alert(self.user.pk, amount)
