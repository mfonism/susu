from django.db import models
from django.utils import timezone


class ShrewdModelManager(models.Manager):
    '''
    I manage shrewd models.

    In my default, shrewd mode I fetch objects (of the 
    managed model) which have been ACTIVATED, and have not been sent 
    into their DELETED state.

    In the non-shrewed mode I fetch every darned object of the model.
    '''
    def __init__(self, *args, **kwargs):
        self.is_shrewd = kwargs.pop('shrewd_mode', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if not self.is_shrewd:
            return ShrewedQuerySet(self.model)
        return ShrewedQuerySet(self.model).filter(
            deleted_at__isnull=True, activated_at__isnull=False
            )


class AbstractShrewdModel(models.Model):
    '''
    I am quite shrewd about the things I'll let you do with me.

    I won't let you delete me unless you really need to. Because 
    once you delete me, I go into nothingness - You can't get me back.
    Which is really risky, especially considering the fact that you 
    often visit your recycle bin to restore things you thought
    you didn't need at some point in time.

    Anyways, the gist is, anytime you call `delete` on me I'll just 
    keep myself out of your way. I'll go into my (safe) deleted state.
    You'll know where to find me when you realise the errors of 
    your ways and feel sorry.
    '''
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = ShrewdModelManager()  # shrewd_mode=True
    all_objects = ShrewdModelManager(shrewd_mode=False)

    def delete(self, hard=False, **kwargs):
        if hard:
            # go into nothingness
            super().delete()
            return
        # deactivate, and go into (safe) deleted state
        self.deleted_at = timezone.now()
        self.activated_at = None 
        self.save()

    def undelete(self):
        # reactivate, and leave deleted state
        self.deleted_at = None
        self.activated_at = timezone.now()
        self.save()


class ShrewedQuerySet(models.QuerySet):
    '''
    I make shrewd operations possible on bulk objects.
    '''
    def delete(self, hard=False, **kwargs):
        if hard:
            # send them all into nothingness
            return super().delete()
        return super().update(deleted_at=timezone.now(), activated_at=None)

    def undelete(self):
        return super().update(deleted_at=None, activated_at=timezone.now())


class ShrewdModelManagerMixin(ShrewdModelManager):
    pass


class AbstractShrewdModelMixin(AbstractShrewdModel):
    class Meta:
        abstract = True
    pass


class ShrewdQuerySetMixin(ShrewedQuerySet):
    pass


class TestAbstractShrewdModelMixin(AbstractShrewdModel):
    pass
