# import dramatiq

from .models import Watch


# @dramatiq.actor
# def reset_watches_on_updated_future_tenure(ft_pk):
#     Watch.objects.filter(tenure__pk=ft_pk).update(status=Watch.TO_REVIEW_UPDATE)

def reset_watches_on_updated_future_tenure(ft_pk):
    Watch.objects.filter(tenure__pk=ft_pk).update(status=Watch.TO_REVIEW_UPDATE)
