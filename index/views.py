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

        context['genres'] = Genre.get_primary_genres(Genre)
        context['languages'] = Language.objects.all()
        context['alphabet'] = string.ascii_uppercase

        # if query string return results
        if q:
            genre = request.GET.get('genre', 'All')
            language = request.GET.get('language', 'All')
            is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
            explicit = is_true(request.GET.get('explicit', 'true'))
            # TODO add switches for these
            show = request.GET.get('show', '24')
            page = request.GET.get('page', 1)

            # if not ajax, include all selected values
            if not request.is_ajax():
                context['selected_q'] = q
                context['selected_genre'] = genre
                context['selected_language'] = language
                context['selected_explicit'] = explicit

            # return podcasts matching search terms
            user = request.user
            podcasts = actual_search(genre, language, explicit, user, q=q)

            paginator = Paginator(podcasts, show)
            try:
                context['podcasts'] = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                context['podcasts'] = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                context['podcasts'] = paginator.page(paginator.num_pages)
            return render(request, 'index/search_results.html', context)

        # else return base
        else:
            return render(request, 'index/search_base.html', context)

def actual_search(genre, language, explicit, user, q=None, alphabet=None):
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
    elif alphabet:
        res = podcasts.filter(title__istartswith=alphabet).order_by('title')
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
    """
    set browse terms
    """
    context = {}
    user = request.user

    if request.method == 'GET':
        context['genres'] = Genre.get_primary_genres(Genre)
        context['languages'] = Language.objects.all()
        context['alphabet'] = string.ascii_uppercase
        context['show'] = [25, 50, 75, 100]

        if request.is_ajax():
            context['selected_alphabet'] = 'A'
            return render(request, 'index/browse_base.html', context)
        else:
            alphabet = request.GET.get('alphabet', 'A')
            show = int(request.GET.get('show', '25'))
            genre = request.GET.get('genre', 'All')
            language = request.GET.get('language', 'All')
            page = request.GET.get('page', 1)
            is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
            explicit = is_true(request.GET.get('explicit', 'true'))

            context['selected_alphabet'] = alphabet
            context['selected_genre'] = genre
            context['selected_language'] = language
            context['selected_explicit'] = explicit
            context['selected_show'] = show

            podcasts = actual_search(genre, language, explicit, user, alphabet=alphabet)

            paginator = Paginator(podcasts, show)
            try:
                context['podcasts'] = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                context['podcasts'] = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                context['podcasts'] = paginator.page(paginator.num_pages)
            return render(request, 'index/browse_results.html', context)

    if request.method == 'POST':
        alphabet = request.POST.get('alphabet', 'A')
        show = request.POST.get('show', '25')
        genre = request.POST.get('genre', 'All')
        language = request.POST.get('language', 'All')
        page = request.POST.get('page', 1)
        is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
        explicit = is_true(request.POST.get('explicit', 'true'))

        context['selected_alphabet'] = alphabet
        podcasts = actual_search(genre, language, explicit, user, alphabet=alphabet)
        paginator = Paginator(podcasts, show)
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
