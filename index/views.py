from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast
from django.core.paginator import Paginator
import string

def navbar(request):
    return render(request, 'navbar.html', {})

def search(request):
    """
    set search terms
    """
    if request.method == 'GET':
        context = {}

        q = request.GET.get('q', None)
        if q and len(q) >= 2:
            abc = request.POST.get('abc', 'A')
            show = request.POST.get('show', '25')
            genre = request.POST.get('genre', 'All')
            language = request.POST.get('language', 'All')
            page = request.POST.get('page', 1)
            is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
            explicit = is_true(request.POST.get('explicit', 'true'))
            user = request.user

            if not request.is_ajax():
                context['genres'] = Genre.get_primary_genres(Genre)
                context['languages'] = Language.objects.all()
                context['abc'] = string.ascii_uppercase

            # return podcasts matching search terms
            podcasts = actual_search(genre, language, explicit, user, q=q)
            paginator = Paginator(podcasts, show)
            context['page_range'] = paginator.page_range
            context['pages'] = paginator.count
            context['podcasts'] = paginator.page(page)
            return render(request, 'search_results.html', context)
        else:
            context['genres'] = Genre.get_primary_genres(Genre)
            context['languages'] = Language.objects.all()
            context['abc'] = string.ascii_uppercase
            return render(request, 'search_base.html', context)

def actual_search(genre, language, explicit, user, q=None, abc=None):
    """
    return matching podcasts, set subscribed to True on subscribed ones
    """

    # get all podcasts
    podcasts = Podcast.objects.all()

    # filter by explicit
    if explicit == False:
        podcasts = podcasts.filter(explicit=explicit)

    # filter by genre
    if genre != 'All':
        podcasts = podcasts.filter(genre__name=genre)

    # filter by language
    if language != 'All':
        podcasts = podcasts.filter(language__name=language)

    # last but not least, filter by title
    # always return n_results
    if q:
        res = podcasts.filter(title__istartswith=q)
    elif abc:
        res = podcasts.filter(title__istartswith=abc).order_by('title')
    else:
        res = {}

    # get a list of itunesids from user's subscriptions (if not AnonymousUser)
    if user.username:
        subscriptions = Subscription.objects.filter(user=user).values_list('itunesid', flat=True)
    else:
        subscriptions = []

    for podcast in res:
        if podcast.itunesid in subscriptions:
            podcast.subscribed = True
    return res

def browse(request):
    context = {}
    user = request.user

    if request.method == 'GET':
        context['genres'] = Genre.get_primary_genres(Genre)
        context['languages'] = Language.objects.all()
        context['abc'] = string.ascii_uppercase
        if request.is_ajax():
            context['selected_abc'] = 'A'
            return render(request, 'index/browse_base.html', context)
        else:
            abc = request.POST.get('abc', 'A')
            show = request.POST.get('show', '25')
            genre = request.POST.get('genre', 'All')
            language = request.POST.get('language', 'All')
            page = request.POST.get('page', 1)
            is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
            explicit = is_true(request.POST.get('explicit', 'true'))

            context['selected_abc'] = abc
            podcasts = actual_search(genre, language, explicit, user, abc=abc)
            paginator = Paginator(podcasts, show)
            context['page_range'] = paginator.page_range
            context['pages'] = paginator.count
            context['podcasts'] = paginator.page(page)
            return render(request, 'index/browse_results.html', context)

    if request.method == 'POST':
        abc = request.POST.get('abc', 'A')
        show = request.POST.get('show', '25')
        genre = request.POST.get('genre', 'All')
        language = request.POST.get('language', 'All')
        page = request.POST.get('page', 1)
        is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
        explicit = is_true(request.POST.get('explicit', 'true'))

        context['selected_abc'] = abc
        podcasts = actual_search(genre, language, explicit, user, abc=abc)
        paginator = Paginator(podcasts, show)
        context['page_range'] = paginator.page_range
        context['pages'] = paginator.count
        context['podcasts'] = paginator.page(page)
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
        if request.is_ajax():
            subscriptions = {}
        else:
            subscriptions = Subscription.get_subscriptions(user)
        return render(request, 'index/subscriptions_base.html', {'subscriptions': subscriptions})

    if request.method == 'POST':
        user = request.user
        subscriptions = Subscription.get_subscriptions(user)
        return render(request, 'index/subscriptions_results.html', {'subscriptions': subscriptions})

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
