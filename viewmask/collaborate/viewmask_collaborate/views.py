from django.shortcuts import render


def index(request):
    return render(request, 'home.html')


def annotate(request):
    return render(request, 'annotate.html')
