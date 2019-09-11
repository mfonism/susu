from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import EsusuGroup, FutureTenure


@receiver(post_save, sender=EsusuGroup)
def assign_hash_id(sender, instance, created, **kwargs):
    '''
    Assign hash id to the created instance using its product key as seed.
    '''
    if not created:
        return
    instance.hash_id = EsusuGroup.get_hash_id(instance.pk)
    instance.save()

@receiver(pre_save, sender=FutureTenure)
def take_hash_id_from_owning_group(sender, instance, **kwargs):
    '''
    Assign hash id from owning group to the instance.
    '''
    instance.hash_id = instance.esusu_group.hash_id
