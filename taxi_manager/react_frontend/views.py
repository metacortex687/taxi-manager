from django.shortcuts import render, get_object_or_404


def hello(request):
    return render(
        request, "hello_world.html"
    )
