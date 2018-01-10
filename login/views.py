from django.shortcuts import render, redirect
from django.http import HttpResponse
from allauth.account import views as allauth
from podcasts.models import Genre, Language, Chart, Subscription, Podcast
import json

ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','#']

# https://stackoverflow.com/questions/26889178/how-to-redirect-all-the-views-in-django-allauth-to-homepage-index-instead-of-ac

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
        errors = {}

        # non-field errors
        for error in data['form']['errors']:
            errors['general'] = error
        # field-specific errors
        for field in data['form']['fields']:
            for error in data['form']['fields'][field]['errors']:
                if field == 'login':
                    field = 'email'
                errors[field] = error
        email = data['form']['fields']['login']['value']

        context = {
            'errors': errors,
            'email': email,
            'view': 'login',
        }

        if ajax:
            if response.status_code == 200:
                return HttpResponse('')
            else:
                return render(request, 'splash.html', context, status=400)
        else:
            context = Chart.get_charts(context)
            context.update({
                'alphabet': ALPHABET,
            })
            if response.status_code == 200:
                return redirect('/')
            else:
                return render(request, 'splash.html', context)
    else:
        return redirect('/?view=login')

def signup(request):
    if request.method == 'POST':
        ajax = request.is_ajax()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = allauth.signup(request)
        data = json.loads(response.content)
        errors = {}

        for error in data['form']['errors']:
            errors['general'] = error
        for field in data['form']['fields']:
            for error in data['form']['fields'][field]['errors']:
                errors[field] = error
        email = data['form']['fields']['email']['value']

        context = {
            'errors': errors,
            'email': email,
            'view': 'signup',
        }

        if ajax:
            if response.status_code == 200:
                return HttpResponse('')
            else:
                return render(request, 'splash.html', context, status=400)
        else:
            context = Chart.get_charts(context)
            context.update({
                'alphabet': ALPHABET,
            })
            if response.status_code == 200:
                return redirect('/')
            else:
                return render(request, 'splash.html', context)
    else:
        return redirect('/?view=signup')

def logout(request):
    if request.method == 'POST':
        response = allauth.logout(request)
        return response

def password_reset(request):
    if request.method == 'POST':
        ajax = request.is_ajax()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = allauth.password_reset(request)
        data = json.loads(response.content)
        errors = {}

        for error in data['form']['errors']:
            errors['general'] = error
        for field in data['form']['fields']:
            for error in data['form']['fields'][field]['errors']:
                errors[field] = error
        email = data['form']['fields']['email']['value']

        context = {
            'errors': errors,
            'email': email,
            'view': 'password',
        }

        if ajax:
            if response.status_code == 200:
                # TODO return "done.html"
                return render(request, 'account/done.html', context)
            else:
                return render(request, 'splash.html', context, status=400)
        else:
            context = Chart.get_charts(context)
            context.update({
                'alphabet': ALPHABET,
            })
            if response.status_code == 200:
                # TODO return "done.html"
                return redirect('/')
            else:
                return render(request, 'splash.html', context)
    else:
        return redirect('/?view=password')

def password_reset_from_key(request, uidb36, key):
    if request.method == 'GET':
        response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
        return response

    if request.method == 'POST':
        response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
        return response
