from .models import Processor


def charge_user(user_pk, amount):
    return Processor.objects.get(user__id=user_pk).charge(amount)

def credit_user(user_pk, amount):
    return Processor.objects.get(user__id=user_pk).credit(amount)
