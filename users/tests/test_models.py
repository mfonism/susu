from django.test import TestCase
from ..models import User


class UserTest(TestCase):
    def test_str_user(self):
        u = User.objects.create_user(email='mfon@eti-mfon.com',
                password='4g8menut!', first_name='Mfon', last_name='Eti-mfon'
        )
        self.assertEqual(str(u), 'Mfon Eti-mfon')

    def test_str_user_with_only_first_name(self):
        u = User.objects.create_user(email='mfon@eti-mfon.com',
                password='4g8menut!', first_name='Mfon'
        )
        self.assertEqual(str(u), 'Mfon <no lastname>')

    def test_str_user_with_only_last_name(self):
        u = User.objects.create_user(email='mfon@eti-mfon.com',
                password='4g8menut!', last_name='Eti-mfon'
        )
        self.assertEqual(str(u), '<no firstname> Eti-mfon')

    def test_str_user_with_no_names(self):
        u = User.objects.create_user(email='mfon@eti-mfon.com', password='4g8menut!')
        self.assertEqual(str(u), '<no firstname> <no lastname>')