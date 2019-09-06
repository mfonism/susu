from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EsusuGroup


@receiver(post_save, sender=EsusuGroup)
def assign_hash_id(sender, instance, created, **kwargs):
    '''
    Assign hash id to the created instance using its product key as seed.
    '''
    if not created:
        return
    instance.hash_id = EsusuGroup.get_hash_id(instance.pk)
    instance.save()
