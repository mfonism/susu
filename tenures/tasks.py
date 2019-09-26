import random

from django.utils import timezone

from .models import (
    FutureTenure, LiveTenure,
    Watch, LiveSubscription,
    Contribution
)
from payments.tasks import charge_user, credit_user


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

def _collect_contribution_from_subscription(ls):
    '''
    To be run as a weekly task.
    Charge the appropriate amount due weekly on the appropriate live tenure
    to the subscribed user, and create contribution object as a receipt of this.
    '''
    alert = charge_user(user_pk=ls.user.pk, amount=ls.tenure.amount)
    if alert.is_success():
        ls.reset_next_charge_date()
        Contribution.objects.create(amount=ls.tenure.amount, tenure=ls.tenure, user=ls.user)
    return alert

def collect_due_weekly_contributions():
    '''
    Collect contributions that are due today.
    '''
    qs = LiveSubscription.objects.filter(next_charge_at__date=timezone.now().date())
    for lsub in qs:
        _collect_contribution_from_subscription(lsub)

collect_due_contributions = collect_due_weekly_contributions
