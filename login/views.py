from django.shortcuts import render, redirect
from django.http import HttpResponse
from allauth.account import views as allauth
from podcasts.models import Genre, Language, Subscription, Podcast
import json

# https://stackoverflow.com/questions/26889178/how-to-redirect-all-the-views-in-django-allauth-to-homepage-index-instead-of-ac

def get_form_errors(data):
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
    try:
        email = data['form']['fields']['login']['value']
    except KeyError:
        email = data['form']['fields']['email']['value']
    return (email, errors)

def login(request):
    """
    relays stuff to and from allauth
    """

    if request.method == 'POST':
        # request sent to allauth is always ajax so the output is json
        ajax = request.is_ajax()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = allauth.login(request)
        # parse json response
        data = json.loads(response.content)
        context = {
            'view': 'login',
        }
        if response.status_code == 200:
            if ajax:
                return render(request, 'dashboard.html', context)
            else:
                return redirect('/')
        else:
            email, errors = get_form_errors(data)
            context.update({
                'errors': errors,
                'email': email,
            })
            if ajax:
                return render(request, 'splash-errors.html', context, status=400)
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
        context = {
            'view': 'signup',
        }

        if response.status_code == 200:
            if ajax:
                return render(request, 'dashboard.html', context)
            else:
                return redirect('/')
        else:
            email, errors = get_form_errors(data)
            context.update({
                'errors': errors,
                'email': email,
            })
            if ajax:
                return render(request, 'splash-errors.html', context, status=400)
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

        if response.status_code == 200:
            context = {
                'view': "login",
                'message': 'We have sent you an e-mail. Please contact us if you do not receive it within a few minutes.',
            }
            if ajax:
                return render(request, 'splash.html', context)
            else:
                return redirect('/')
        else:
            email, errors = get_form_errors(data)
            context = {
            'view': 'password',
            'errors': errors,
            'email': email,
            }
            if ajax:
                return render(request, 'splash-errors.html', context, status=400)
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
