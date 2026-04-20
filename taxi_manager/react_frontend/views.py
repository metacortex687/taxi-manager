from django.shortcuts import render, get_object_or_404


def index(request, subpath=""):
    return render(
        request, "react_frontend/index.html"
    )
