from django.test import TestCase
from django.contrib.auth import get_user_model

from tenures.models import EsusuGroup


User = get_user_model()


class EsusuGroupTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.eg = EsusuGroup.objects.create(
            name='Happy Pockets', admin=self.user
        )

    def test_has_hash_id_on_creation(self):
        '''
        Assert that group is assigned hash id on creation.
        '''
        self.assertIsNotNone(self.eg.hash_id)
        self.assertNotEqual(self.eg.hash_id, '')

    def test_hash_id_is_at_least_11_chars(self):
        '''
        Assert that hash id is at least 11-character long.
        '''
        self.assertGreaterEqual(len(self.eg.hash_id), 11)
