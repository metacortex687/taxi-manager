from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect, get_token

def index(request):
    return render(request, "index.html", {})

def test_csrf_protect(request):
    return render(request, "test_csrf_protect.html", {})