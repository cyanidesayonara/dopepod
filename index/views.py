from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast
from django.views.generic import ListView
import string

class IndexListView(ListView):
    queryset = Podcast.objects.filter(title__istartswith='a').order_by('title')
    context_object_name = 'podcasts'

    def get(self, request):
        genres = Genre.get_primary_genres(Genre)
        languages = Language.objects.all()
        abc = string.ascii_uppercase
        podcasts = Podcast.objects.filter(title__istartswith='a').order_by('title')
        context = {'genres': genres, 'languages': languages, 'abc': abc, 'podcasts': podcasts}
        return render(request, 'index/browse.html', context)

def home(request):
    genres = Genre.get_primary_genres(Genre)
    languages = Language.objects.all()
    abc = string.ascii_uppercase
    context = {'genres': genres, 'languages': languages, 'abc': abc}

    # import logging
    # logger = logging.getLogger(__name__)
    # logger.error('whaddup')

    if request.method == "GET":
        return render(request, 'index/index.html', context)

    # any other method not accepted
    else:
        raise Http404()

def navbar(request):
    return render(request, 'navbar.html', {})

@login_required
def subscriptions(request):
    """
    returns subscription for user
    GET for non-ajax requests
    GET ajax request first returns base.html,
    then requests subscriptions via POST
    """

    if request.method == 'GET':
        user = request.user
        subscriptions = Subscription.get_subscriptions(user)
        return render(request, 'index/subscriptions.html', {'subscriptions': subscriptions})

@login_required
def settings(request):
    """
    GET return settings form
    POST save settings form
    """

    if request.method == 'GET':
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return render(request, 'index/settings.html', {
            'user_form': user_form,
            'profile_form': profile_form
            })

    if request.method == 'POST':
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, instance=request.user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                return render(request, 'index/settings.html', {
                    'user_form': user_form,
                    'profile_form': profile_form
                    })

            else:
                return render(request, 'index/settings.html', {
                    'user_form': user_form,
                    'profile_form': profile_form
                    })
