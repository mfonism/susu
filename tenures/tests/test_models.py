from django.test import TestCase
from django.contrib.auth import get_user_model

from tenures.models import EsusuGroup, FutureTenure


class EsusuGroupTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.eg = EsusuGroup.objects.create(name='Happy Pockets', admin=self.user)
        self.eg.refresh_from_db()

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


class FutureTenureTest(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.eg = EsusuGroup.objects.create(name='Lifelong Savers', admin=self.user)
        self.ft = FutureTenure.objects.create(amount=5000, esusu_group=self.eg)
        self.ft.refresh_from_db()

    def test_takes_group_hash_id_on_creations(self):
        '''
        Assert that future tenure takes on the hash id of its owning group.
        '''
        self.assertEqual(self.ft.hash_id, self.eg.hash_id)
