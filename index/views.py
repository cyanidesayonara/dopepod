from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from index.models import Profile
from podcasts.models import Genre, Language, Subscription
import logging

logger = logging.getLogger(__name__)

def home(request):
    genres = Genre.get_primary_genres(Genre)
    languages = Language.objects.all()
    logger.error('whaddup')
    if request.method == 'GET':
        return render(request, 'index/index.html', {'genres': genres, 'languages': languages})
    else:
        return render(request, 'index/ajax_index.html', {'genres': genres, 'languages': languages})

def navbar(request):
    logger.error('whaddup')
    return render(request, 'navbar.html', {})

def subscriptions(request):
    """
    returns subscription for user
    """
    user = request.user
    subscriptions = {}
    if user.is_authenticated():
        subscriptions = Subscription.objects.filter(user=user)
    if request.method == 'GET':
        return render(request, 'subscriptions.html', {'subscriptions': subscriptions})
    else:
            return render(request, 'ajax_subscriptions.html', {'subscriptions': subscriptions})

@transaction.atomic
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return render(request, 'index/profile.html', {})
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'index/ajax_edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
        })

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    return render(request, 'index/profile.html', {'user': user, 'profile': profile})
