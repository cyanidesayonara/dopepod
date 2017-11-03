from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from index.models import Profile
from podcasts.models import Genre, Language
import logging

logger = logging.getLogger(__name__)

def home(request):
    genres = Genre.get_primary_genres(Genre)
    languages = Language.objects.all()
    logger.error('whaddup')
    return render(request, 'index/index.html', {'genres': genres, 'languages': languages})

def navbar(request):
    logger.error('whaddup')
    return render(request, 'navbar.html', {})

@transaction.atomic
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile', username=request.user)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'index/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
        })

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    return render(request, 'index/profile.html', {'user': user, 'profile': profile})

