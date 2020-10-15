from django.http import JsonResponse
from django.views.decorators.http import require_POST

from pontoon.base.utils import require_AJAX
from pontoon.tour.forms import UserTourStatusForm


@require_AJAX
@require_POST
def update_tour_status(request):
    """Update User tour status."""
    form = UserTourStatusForm(request.POST, instance=request.user.profile,)

    if not form.is_valid():
        return JsonResponse(
            {
                "status": False,
                "message": "Bad Request: {error}".format(error=form.errors),
            },
            status=400,
        )

    form.save()

    return JsonResponse({"status": True})
