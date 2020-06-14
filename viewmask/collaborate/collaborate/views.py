# from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    if request.user.is_authenticated:
        # Do something for authenticated users.
        pass
    else:
        # Do something for anonymous users.
        pass
    return HttpResponse('auth' if request.user.is_authenticated else 'no auth')


def annotate(request):
    return HttpResponse('annotate')
