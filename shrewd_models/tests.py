from django.test import TestCase

from .models import AbstractShrewdModel, ShrewdModel


class AbstractShrewdModelTest(TestCase):

    def test_abstract_shrewd_model_is_abstract(self):
        with self.assertRaises(AttributeError) as e:
            AbstractShrewdModel.objects.create()
        expected_error_msg = 'Manager isn\'t available; AbstractShrewdModel is abstract'
        self.assertEqual(e.exception.args[0], expected_error_msg)
        

class ShrewdModelTest(TestCase):

    def setUp(self):
        self.shmo1 = ShrewdModel.objects.create()
        self.shmo2 = ShrewdModel.objects.create()
        self.shmo3 = ShrewdModel.objects.create()
        self.shmo4 = ShrewdModel.objects.create()
        self.shmo5 = ShrewdModel.objects.create()
        self.shmo6 = ShrewdModel.objects.create()
        self.shmo7 = ShrewdModel.objects.create()

    def test_delete_is_soft_by_default(self):
        pk4 = self.shmo4.pk
        self.shmo4.delete()

        self.assertFalse(ShrewdModel.objects.filter(pk=pk4).exists())
        self.assertTrue(ShrewdModel.all_objects.filter(pk=pk4).exists())

    def test_undelete(self):
        pk4 = self.shmo4.pk
        self.shmo4.delete()
        self.shmo4.undelete()
        
        self.assertTrue(ShrewdModel.objects.filter(pk=pk4).exists())
        self.assertTrue(ShrewdModel.all_objects.filter(pk=pk4).exists())

    def test_bulk_delete_is_soft_by_default(self):
        ShrewdModel.objects.filter(pk__lt=4).delete()

        self.assertFalse(ShrewdModel.objects.filter(pk__lt=4).exists())
        self.assertTrue(ShrewdModel.all_objects.filter(pk__lt=4).exists())

    def test_bulk_undelete(self):
        # undelete on `all_objects`, as they no longer exist on `objects`
        ShrewdModel.objects.filter(pk__lt=4).delete()
        ShrewdModel.all_objects.filter(pk__lt=4).undelete()
        
        self.assertTrue(ShrewdModel.objects.filter(pk__lt=4).exists())
        self.assertTrue(ShrewdModel.all_objects.filter(pk__lt=4).exists())

    def test_hard_delete(self):
        pk4 = self.shmo4.pk
        self.shmo4.delete(hard=True)

        self.assertFalse(ShrewdModel.objects.filter(pk=pk4).exists())
        self.assertFalse(ShrewdModel.all_objects.filter(pk=pk4).exists())

    def test_cannot_exactly_undelete_hard_delete(self):
        pk4 = self.shmo4.pk
        ca4 = self.shmo4.created_at
        self.shmo4.delete(hard=True)
        self.shmo4.undelete()

        self.assertFalse(ShrewdModel.objects.filter(pk=pk4).exists())
        self.assertFalse(ShrewdModel.all_objects.filter(pk=pk4).exists())
        # however, new and equal object has been added!
        # so be careful about undeleting already hard deleted single objects
        self.assertEqual(ShrewdModel.objects.count(), 7)

    def test_bulk_hard_delete(self):
        ShrewdModel.objects.filter(pk__lt=4).delete(hard=True)

        self.assertFalse(ShrewdModel.objects.filter(pk__lt=4).exists())
        self.assertFalse(ShrewdModel.all_objects.filter(pk__lt=4).exists())

    def test_cannot_by_any_means_undelete_bulk_hard_delete(self):
        # because you've already consumed the queryset, and
        # the objects no longer exist on either `objects` or `all_objects`
        ShrewdModel.objects.filter(pk__lt=4).delete(hard=True)
        ShrewdModel.objects.filter(pk__lt=4).undelete()
        
        self.assertFalse(ShrewdModel.objects.filter(pk__lt=4).exists())
        self.assertFalse(ShrewdModel.all_objects.filter(pk__lt=4).exists())
        # no new objects, however, are added
        self.assertEqual(ShrewdModel.objects.count(), 4)
