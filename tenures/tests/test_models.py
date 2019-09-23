from django.test import TestCase
from django.contrib.auth import get_user_model

from tenures.models import (
    EsusuGroup,
    FutureTenure, LiveTenure,
    Watch, LiveSubscription
)


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


class EsusuGroupMembershipTest(TestCase):
    '''
    A user is a member of a group if they are either the admin or
    they are watching its future tenure or
    they are subscribed to its live tenure.
    '''
    def setUp(self):
        self.mfon = get_user_model().objects.create_user(
            email='mfon@etimfon.com', password='4g8menut!',
            first_name='Mfon', last_name='Eti-mfon'
        )
        self.group = EsusuGroup.objects.create(
            name='Lifelong Savers', admin=self.mfon
        )

        self.ambrose = get_user_model().objects.create_user(
            email='ambrose@igibo.com', password='nopassword',
            first_name='Ambrose', last_name='Igibo'
        )
        self.bryan = get_user_model().objects.create_user(
            email='Bryan@stclaire.com', password='passwordless',
            first_name='Bryan', last_name='StClaire'
        )

    def test_admin_is_member(self):
        '''
        Being the admin, Mfon is a member of the group.
        '''
        self.assertTrue(self.group.has_member(self.mfon))

    def test_has_watching_member(self):
        '''
        Ambrose becomes a member once he places a watch on group's ft.
        '''
        ft = FutureTenure.objects.create(esusu_group=self.group, amount=5000)
        self.assertFalse(self.group.has_member(self.ambrose))

        Watch.objects.create(user=self.ambrose, tenure=ft)

        self.assertTrue(self.group.has_watching_member(self.ambrose))
        self.assertTrue(self.group.has_member(self.ambrose))

    def test_has_live_member(self):
        '''
        Ambrose becomes a member once he's subscribed to a live tenure.
        '''
        lt = LiveTenure.objects.create(esusu_group=self.group, amount=5000)
        self.assertFalse(self.group.has_member(self.bryan))

        LiveSubscription.objects.create(user=self.ambrose, tenure=lt)

        self.assertTrue(self.group.has_live_member(self.ambrose))
        self.assertTrue(self.group.has_member(self.ambrose))


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
