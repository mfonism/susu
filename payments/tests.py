from django.contrib.auth import get_user_model
from django.test import TestCase
from hashids import Hashids

from .models import Processor
from .tasks import charge_user, credit_user


class TestTasks(TestCase):

    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        Processor.objects.create(
            user=self.mfon, card_type=Processor.MASTER_CARD,
            card_id=Hashids(min_length=32).encode(self.mfon.pk),
        )

    def test_charge_user(self):
        resp = charge_user(user_pk=self.mfon.pk, amount=10000)

        self.assertTrue(resp.is_success())
        self.assertTrue(resp.is_charge())
        self.assertEqual(resp.user_pk, self.mfon.pk)
        self.assertEqual(resp.amount, 10000)

    def test_credit_user(self):
        resp = credit_user(user_pk=self.mfon.pk, amount=50000)

        self.assertTrue(resp.is_success())
        self.assertTrue(resp.is_credit())
        self.assertEqual(resp.user_pk, self.mfon.pk)
        self.assertEqual(resp.amount, 50000)
