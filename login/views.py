from django.shortcuts import render, redirect
from django.http import HttpResponse
from allauth.account import views as allauth
from podcasts.models import Genre, Language, Chart, Subscription, Podcast
import json

ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','#']

def login(request):
    """
    relays stuff to and from allauth
    """

    if request.method == 'POST':
        # request sent to allauth is always ajax
        ajax = request.is_ajax()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = allauth.login(request)

        # parse json response
        data = json.loads(response.content)
        errors = ''
        for error in data['form']['errors']:
            errors = errors + error
        for field in data['form']['fields']:
            for error in data['form']['fields'][field]['errors']:
                errors = errors + error


        if ajax:
            if response.status_code == 200:
                return HttpResponse('')
            else:
                return HttpResponse(errors, status=400)

        else:
            chart = Chart.objects.get(genre=None)
            genres = Genre.get_primary_genres()
            email = data['form']['fields']['login']['value']
            context = {
                'extend': True,
                'errors': errors,
                'email': email,
                'chart_genres': genres,
                'chart': chart,
                'alphabet': ALPHABET,
            }
            if response.status_code == 200:
                return redirect('/')
            else:
                return render(request, 'splash.html', context)

def signup(request):
    if request.method == 'POST':
        ajax = request.is_ajax()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = allauth.signup(request)
        data = json.loads(response.content)

        errors = ''
        for error in data['form']['errors']:
            errors = errors + error
        for field in data['form']['fields']:
            for error in data['form']['fields'][field]['errors']:
                errors = errors + error

        if ajax:
            if response.status_code == 200:
                return HttpResponse('')
            else:
                return HttpResponse(errors, status=400)
        else:
            chart = Chart.objects.get(genre=None)
            genres = Genre.get_primary_genres()
            email = data['form']['fields']['login']['value']
            context = {
                'signup': True,
                'extend': True,
                'errors': errors,
                'email': email,
                'chart_genres': genres,
                'chart': chart,
                'alphabet': ALPHABET,
            }
            if response.status_code == 200:
                return redirect('/')
            else:
                return render(request, 'splash.html', context)

def password_reset(request):
    if request.method == 'POST':
        ajax = request.is_ajax()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = allauth.password_reset(request)
        data = json.loads(response.content)

        errors = ''
        for error in data['form']['errors']:
            errors = errors + error
        for field in data['form']['fields']:
            for error in data['form']['fields'][field]['errors']:
                errors = errors + error

        if ajax:
            if response.status_code == 200:
                return HttpResponse('')
            else:
                return HttpResponse(errors, status=400)
        else:
            chart = Chart.objects.get(genre=None)
            genres = Genre.get_primary_genres()
            email = data['form']['fields']['login']['value']
            context = {
                'signup': True,
                'extend': True,
                'errors': errors,
                'email': email,
                'chart_genres': genres,
                'chart': chart,
                'alphabet': ALPHABET,
            }
            if response.status_code == 200:
                return redirect('/')
            else:
                return render(request, 'splash.html', context)

def logout(request):
    if request.method == 'POST':
        response = allauth.logout(request)
        return response
