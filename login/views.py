from django.shortcuts import render
from allauth.account import views as allauth
import json

def login(request):
    """
    relays stuff to and from allauth
    """

    if request.method == 'POST':
        ajax = request.is_ajax()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = allauth.login(request)
        data = json.loads(response.content)
        errors = data['form']['errors']

        context = {
            'errors': errors,
        }

        if ajax:
            if response.status_code == '200':
                return render(request, 'ajax.html', {})
            else:
                print(data['html'])
                return response
        else:
            context.update({
                'extend': True,
            })
            if response.status_code == '200':
                return redirect('/')
            else:
                return render(request, 'login.html', context)

def signup(request):
    response = allauth.signup(request)
    print(response.content)

def password_reset(request):
    response = allauth.password_reset(request)
    print(response.content)

def logout(request):
    if request.method == 'POST':
        response = allauth.logout(request)
        return response
