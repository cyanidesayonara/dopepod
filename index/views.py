from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast
from django.core.paginator import Paginator
import string

def navbar(request):
    return render(request, 'navbar.html', {})

def home(request):
    user = request.user
    context = {}
    context['alphabet'] = string.ascii_uppercase
    context['search'] = True
    context['selected_alphabet'] = 'A'
    context['chart'] = Podcast.get_chart(user)

    return render(request, 'index/index.html', context)

def search(request):
    """
    set search terms
    """
    if request.method == 'GET':
        context = {}

        q = request.GET.get('q', None)

        # if query string, return results
        if q:
            context['genres'] = Genre.get_primary_genres()
            context['languages'] = Language.objects.all()
            context['alphabet'] = string.ascii_uppercase
            context['search'] = True

            genre = request.GET.get('genre', 'All')
            language = request.GET.get('language', 'All')
            is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
            explicit = is_true(request.GET.get('explicit', 'true'))
            show = request.GET.get('show', 'detail')
            page = request.GET.get('page', 1)

            context['selected_alphabet'] = 'A'
            context['selected_show'] = show
            context['selected_genre'] = genre
            context['selected_language'] = language
            context['selected_explicit'] = explicit

            # if not ajax, include all selected values
            if not request.is_ajax():
                context['selected_q'] = q

            # return podcasts matching search terms
            user = request.user
            podcasts = actual_search(genre, language, explicit, user, q=q)

            if show == 'detail':
                paginator = Paginator(podcasts, 24)
            else:
                paginator = Paginator(podcasts, 50)

            try:
                context['podcasts'] = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                context['podcasts'] = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                context['podcasts'] = paginator.page(paginator.num_pages)

            if show == 'detail':
                return render(request, 'index/results_detail.html', context)
            else:
                return render(request, 'index/results_list.html', context)

        # else return base
        else:
            return redirect('/')

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
    res = {}
    if q:
        res1 = podcasts.filter(title__istartswith=q)
        res2 = podcasts.filter(title__icontains=q)
        res = res1.union(res2).order_by('title')
    elif alphabet:
        res = podcasts.filter(title__istartswith=alphabet).order_by('title')

    # get a list of itunesids from user's subscriptions (if not AnonymousUser)
    subscriptions = []
    if user.username:
        subscriptions = Subscription.objects.filter(user=user).values_list('itunesid', flat=True)

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
        # show browse bar
        context['browse'] = True
        context['alphabet'] = string.ascii_uppercase

        # for ajax, just return base
        if request.is_ajax():
            context['selected_alphabet'] = 'A'
            context['selected_show'] = 'list'
            return render(request, 'index/index.html', context)
        else:
            context['genres'] = Genre.get_primary_genres()
            context['languages'] = Language.objects.all()

            alphabet = request.GET.get('alphabet', 'A')
            genre = request.GET.get('genre', 'All')
            language = request.GET.get('language', 'All')
            show = request.GET.get('show', 'list')
            page = request.GET.get('page', 1)
            is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
            explicit = is_true(request.GET.get('explicit', 'true'))

            context['selected_alphabet'] = alphabet
            context['selected_genre'] = genre
            context['selected_language'] = language
            context['selected_explicit'] = explicit
            context['selected_show'] = show

            podcasts = actual_search(genre, language, explicit, user, alphabet=alphabet)

            if show == 'detail':
                paginator = Paginator(podcasts, 24)
            else:
                paginator = Paginator(podcasts, 50)

            try:
                context['podcasts'] = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                context['podcasts'] = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                context['podcasts'] = paginator.page(paginator.num_pages)

            if show == 'detail':
                return render(request, 'index/results_detail.html', context)
            else:
                return render(request, 'index/results_list.html', context)

    if request.method == 'POST':
        context['genres'] = Genre.get_primary_genres()
        context['languages'] = Language.objects.all()
        context['alphabet'] = string.ascii_uppercase

        alphabet = request.POST.get('alphabet', 'A')
        genre = request.POST.get('genre', 'All')
        language = request.POST.get('language', 'All')
        show = request.POST.get('show', 'list')
        page = request.POST.get('page', 1)
        is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
        explicit = is_true(request.POST.get('explicit', 'true'))

        context['selected_alphabet'] = alphabet
        context['selected_genre'] = genre
        context['selected_language'] = language
        context['selected_explicit'] = explicit
        context['selected_show'] = show

        podcasts = actual_search(genre, language, explicit, user, alphabet=alphabet)

        if show == 'detail':
            paginator = Paginator(podcasts, 24)
        else:
            paginator = Paginator(podcasts, 50)

        try:
            context['podcasts'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['podcasts'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['podcasts'] = paginator.page(paginator.num_pages)

        if show == 'detail':
            return render(request, 'index/results_detail.html', context)
        else:
            return render(request, 'index/results_list.html', context)

def subscriptions(request):
    """
    returns subscription for user
    GET for non-ajax requests
    GET ajax request first returns base.html,
    then requests subscriptions via POST
    """

    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            context = {}
            context['search'] = True

            if request.is_ajax():
                return render(request, 'index/index.html', context)
            else:
                context['subscriptions'] = Subscription.get_subscriptions(user)
                return render(request, 'index/subscriptions.html', context)

        if request.method == 'POST':
            context = {}
            context['subscriptions']  = Subscription.get_subscriptions(user)
            return render(request, 'index/subscriptions.html', context)
    else:
        raise Http404()

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
