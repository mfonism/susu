from django.db import connection
from django.db.models.base import ModelBase
from django.test import TestCase, TransactionTestCase

from .models import AbstractShrewdModel, AbstractShrewdModelMixin


class AbstractionTest(TestCase):

    def test_abstract_shrewd_model_is_abstract(self):
        with self.assertRaises(AttributeError) as e:
            AbstractShrewdModel.objects.create()
        expected_error_msg = 'Manager isn\'t available; AbstractShrewdModel is abstract'
        self.assertEqual(e.exception.args[0], expected_error_msg)

    def test_abstract_shrewd_model_mixin_is_abstract(self):
        with self.assertRaises(AttributeError) as e:
            AbstractShrewdModelMixin.objects.create()
        expected_error_msg = 'Manager isn\'t available; AbstractShrewdModelMixin is abstract'
        self.assertEqual(e.exception.args[0], expected_error_msg)        
        

class NonAbstractionTest(TransactionTestCase):

    mixin = AbstractShrewdModelMixin

    @classmethod
    def setUpClass(cls):
        cls.model_cls = ModelBase(
            f'__TestModel__{cls.mixin.__name__}',
            (cls.mixin,),
            {'__module__': cls.mixin.__module__}
        )
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        pass

    def setUp(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(self.model_cls)

        self.shmo1 = self.model_cls.objects.create()
        self.shmo2 = self.model_cls.objects.create()
        self.shmo3 = self.model_cls.objects.create()
        self.shmo4 = self.model_cls.objects.create()
        self.shmo5 = self.model_cls.objects.create()
        self.shmo6 = self.model_cls.objects.create()
        self.shmo7 = self.model_cls.objects.create()

    def tearDown(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(self.model_cls)

    def test_delete_is_soft_by_default(self):
        pk4 = self.shmo4.pk
        self.shmo4.delete()

        self.assertFalse(self.model_cls.objects.filter(pk=pk4).exists())
        self.assertTrue(self.model_cls.all_objects.filter(pk=pk4).exists())

    def test_undelete(self):
        pk4 = self.shmo4.pk
        self.shmo4.delete()
        self.shmo4.undelete()
        
        self.assertTrue(self.model_cls.objects.filter(pk=pk4).exists())
        self.assertTrue(self.model_cls.all_objects.filter(pk=pk4).exists())

    def test_bulk_delete_is_soft_by_default(self):
        self.model_cls.objects.filter(pk__lt=4).delete()

        self.assertFalse(self.model_cls.objects.filter(pk__lt=4).exists())
        self.assertTrue(self.model_cls.all_objects.filter(pk__lt=4).exists())

    def test_bulk_undelete(self):
        # undelete on `all_objects`, as they no longer exist on `objects`
        self.model_cls.objects.filter(pk__lt=4).delete()
        self.model_cls.all_objects.filter(pk__lt=4).undelete()
        
        self.assertTrue(self.model_cls.objects.filter(pk__lt=4).exists())
        self.assertTrue(self.model_cls.all_objects.filter(pk__lt=4).exists())

    def test_hard_delete(self):
        pk4 = self.shmo4.pk
        self.shmo4.delete(hard=True)

        self.assertFalse(self.model_cls.objects.filter(pk=pk4).exists())
        self.assertFalse(self.model_cls.all_objects.filter(pk=pk4).exists())

    def test_cannot_exactly_undelete_hard_delete(self):
        pk4 = self.shmo4.pk
        ca4 = self.shmo4.created_at
        self.shmo4.delete(hard=True)
        self.shmo4.undelete()

        self.assertFalse(self.model_cls.objects.filter(pk=pk4).exists())
        self.assertFalse(self.model_cls.all_objects.filter(pk=pk4).exists())
        # however, new and equal object has been added!
        # so be careful about undeleting already hard deleted single objects
        self.assertEqual(self.model_cls.objects.count(), 7)

    def test_bulk_hard_delete(self):
        self.model_cls.objects.filter(pk__lt=4).delete(hard=True)

        self.assertFalse(self.model_cls.objects.filter(pk__lt=4).exists())
        self.assertFalse(self.model_cls.all_objects.filter(pk__lt=4).exists())

    def test_cannot_by_any_means_undelete_bulk_hard_delete(self):
        # because you've already consumed the queryset, and
        # the objects no longer exist on either `objects` or `all_objects`
        self.model_cls.objects.filter(pk__lt=4).delete(hard=True)
        self.model_cls.objects.filter(pk__lt=4).undelete()
        
        self.assertFalse(self.model_cls.objects.filter(pk__lt=4).exists())
        self.assertFalse(self.model_cls.all_objects.filter(pk__lt=4).exists())
        # no new objects, however, are added
        self.assertEqual(self.model_cls.objects.count(), 4)
