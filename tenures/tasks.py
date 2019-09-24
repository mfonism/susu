import random

from .models import FutureTenure, LiveTenure, Watch, LiveSubscription


def reset_watches_on_updated_future_tenure(ft_pk):
    Watch.objects.filter(tenure__pk=ft_pk).update(
        status=Watch.TO_REVIEW_UPDATE
    )

def promote_future_tenure(ft_pk):
    '''
    Promote a Future Tenure to a Live Tenure.
    '''
    ft = FutureTenure.objects.get(pk=ft_pk)

    # create live tenure
    lt = LiveTenure.objects.create(
        amount=ft.amount, esusu_group=ft.esusu_group
    )
    # populate live tenure with live subscriptions created from
    # watches that have opted into promoted future tenure
    # creation of live subscriptions should be random
    watches = list(Watch.objects.filter(tenure=ft, status=Watch.OPTED_IN))
    random.shuffle(watches)
    for watch in watches:
        LiveSubscription.objects.create(
            tenure=lt, user=watch.user
        )

    # delete future tenure
    # and associated watches
    Watch.objects.filter(tenure=ft).delete(hard=True)
    ft.delete(hard=True)
