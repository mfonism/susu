import dramatiq

from .models import Watch


@dramatiq.actor
def reset_watches_on_updated_future_tenure(ft):
    ft.watches.update(status=Watch.TO_REVIEW_UPDATE)
