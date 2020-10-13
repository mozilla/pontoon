from django.conf import settings


def globals(request):
    return {"request": request, "settings": settings}
