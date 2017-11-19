from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast
import string

# def home(request):
#     context = {}
#     context['genres'] = Genre.get_primary_genres(Genre)
#     context['languages'] = Language.objects.all()
#
#     # import logging
#     # logger = logging.getLogger(__name__)
#     # logger.error('whaddup')
#
#     if request.method == "GET":
#         return render(request, 'index/index.html', context)
#
#     # any other method not accepted
#     else:
#         raise Http404()

def navbar(request):
    return render(request, 'navbar.html', {})

def browse(request):
    context = {}
    context['genres'] = Genre.get_primary_genres(Genre)
    context['languages'] = Language.objects.all()
    context['abc'] = string.ascii_uppercase
    return render(request, 'index/browse_base.html', context)

def browse_results(request):
    try:
        abc = request.GET['abc']
    except KeyError:
        abc = 'A'

    try:
        show = int(request.GET['show'])
    except KeyError:
        show = 10

    try:
        genre = request.GET['genre']
    except KeyError:
        genre = 'All'

    try:
        language = request.GET['language']
    except KeyError:
        language = 'All'

    try:
        explicit = False if request.GET['explicit'] == 'false' else True
    except:
        explicit = True


    context = {}
    if not request.is_ajax():
        context = {}
        context['genres'] = Genre.get_primary_genres(Genre)
        context['languages'] = Language.objects.all()
        context['abc'] = string.ascii_uppercase
        context['selected_abc'] = abc
    context['breadcrumbs'] = [genre, abc]
    context['podcasts'] = Podcast.objects.filter(title__istartswith=abc).order_by('title')[:show]
    return render(request, 'index/browse_results.html', context)

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
