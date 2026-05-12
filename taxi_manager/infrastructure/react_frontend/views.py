from django.shortcuts import render, get_object_or_404
from django.conf import settings


def index(request, subpath=""):

    return render(
        request,
        "react_frontend/index.html",
        {
            "USE_VITE_DEV_SERVER": settings.USE_VITE_DEV_SERVER == "True"
        },
    )
