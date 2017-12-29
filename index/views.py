from django.shortcuts import render, redirect, Http404, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from allauth.account import views as allauth
import json

ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','#']

def navbar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == 'GET':
        return render(request, 'navbar.html', {})

def login(request):
    """
    relays stuff to and from allauth
    """

    if request.method == 'POST':
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = allauth.login(request)
        data = json.loads(response.content)
        errors = data['form']['errors']

        context = {
            'errors': errors,
        }

        if request.is_ajax():
            if response.status_code == '200':
                return render(request, 'ajax.html', {})        
            else:
                print(request.is_ajax())
                return render(request, 'errors.html', context)
        else:
            if response.status_code == '200':
                return redirect('/')
            else:
                return render(request, 'dashboard.html', context)

def signup(request):
    response = allauth.login(request)
    print(response.content)

def reset_password(request):
    response = allauth.login(request)
    print(response.content)

def index(request):
    """
    returns index page
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        signup = request.GET.get('signup' , None)
        subscriptions = Subscription.get_subscriptions(user)

        context = {
            'subscriptions': subscriptions,
            'signup': signup,
        }

        if request.is_ajax():
            if user.is_authenticated:
                return render(request, 'dashboard.html', context)
            else:
                return render(request, 'login.html', context)

        # chart and search bar for non-ajax
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts()
        chart_header = 'Top 50 podcasts on iTunes'

        context.update({
            'dashboard': True,
            'chart_header': chart_header,
            'chart_genres': genres,
            'chart': chart[:50],
            'alphabet': ALPHABET,
        })
        
        if user.is_authenticated:
            return render(request, 'dashboard.html', context)
        else:
            return render(request, 'login.html', context)

def charts(request):
    """
    returns chart (optional: for requested genre)
    with search bar for non-ajax
    """

    if request.method == 'GET':
        genre = request.GET.get('genre', None)
        user = request.user
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts(genre)
        chart_header = 'Top 50 podcasts on iTunes'

        context = {
            'chart': chart[:50],
            'chart_genres': genres,
            'chart_selected_genre': genre,
            'chart_header': chart_header,
        }

        if request.is_ajax():
            return render(request, 'charts.html', context)

        subscriptions = Subscription.get_subscriptions(user)

        # search bar + subs for non-ajax
        context.update({
            'subscriptions': subscriptions,
            'alphabet': ALPHABET,
        })

        return render(request, 'base.html', context)

def search(request):
    """
    sets search terms
    calls search
    returns results
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        q = request.GET.get('q', None)
        genre = request.GET.get('genre', None)
        language = request.GET.get('language', None)

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        languages = Language.objects.all()
        genres = Genre.get_primary_genres()

        podcasts = Podcast.search(genre, language, user, q=q)
        paginator = Paginator(podcasts, 60)

        if paginator.count == 1:
            results_header = str(paginator.count) + ' result'
        else:
            results_header = str(paginator.count) + ' results'

        try:
            podcasts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            podcasts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            podcasts = paginator.page(paginator.num_pages)

        context = {
            'genres': genres,
            'languages': languages,
            'selected_q': q,
            'selected_genre': genre,
            'selected_language': language,
            'results_header': results_header,
            'podcasts': podcasts,
        }

        if request.is_ajax():
            return render(request, 'results_detail.html', context)

        chart = Podcast.get_charts()
        chart_header = 'Top 50 podcasts on iTunes'
        subscriptions = Subscription.get_subscriptions(user)

        context.update({
            'subscriptions': subscriptions,
            'chart_genres': genres,
            'chart': chart[:50],
            'alphabet': ALPHABET,
            'chart_header': chart_header,
        })

        return render(request, 'results_detail.html', context)

def browse(request):
    """
    sets browse terms
    calls search
    returns results
    with chart & browse bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        alphabet = request.GET.get('q', None)
        genre = request.GET.get('genre', None)
        language = request.GET.get('language', None)

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        languages = Language.objects.all()
        genres = Genre.get_primary_genres()

        podcasts = Podcast.search(genre, language, user, alphabet=alphabet)
        paginator = Paginator(podcasts, 160)

        if paginator.count == 1:
            results_header = str(paginator.count) + ' result'
        else:
            results_header = str(paginator.count) + ' results'

        try:
            podcasts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            podcasts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            podcasts = paginator.page(paginator.num_pages)

        context = {
            'genres': genres,
            'languages': languages,
            'selected_alphabet': alphabet,
            'selected_genre': genre,
            'selected_language': language,
            'results_header': results_header,
            'podcasts': paginator,
            'podcasts1': podcasts[:40],
            'podcasts2': podcasts[40:80],
            'podcasts3': podcasts[80:120],
            'podcasts4': podcasts[120:160],
        }

        if request.is_ajax():
            return render(request, 'results_list.html', context)

        # chart & browse bar for non-ajax
        chart = Podcast.get_charts()
        chart_header = 'Top 50 podcasts on iTunes'
        subscriptions = Subscription.get_subscriptions(user)

        context.update({
            'subscriptions': subscriptions,
            'chart_genres': genres,
            'chart': chart[:50],
            'alphabet': ALPHABET,
            'chart_header': chart_header,
        })
        return render(request, 'results_list.html', context)

def subscriptions(request):
    """
    returns subscriptions for user
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        subscriptions = Subscription.get_subscriptions(user)

        if subscriptions.count == 1:
            results_header = str(subscriptions.count()) + ' subscription'
        else:
            results_header = str(subscriptions.count()) + ' subscriptions'


        context = {
            'results_header': results_header,
            'subscriptions': subscriptions,
        }

        if request.is_ajax():
            return render(request, 'subscriptions.html', context)

        # chart & search bar for non-ajax
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts()
        chart_header = 'Top 50 podcasts on iTunes'


        context.update({
            'chart_genres': genres,
            'chart': chart[:50],
            'alphabet': ALPHABET,
            'chart_header': chart_header,
        })
        return render(request, 'subscriptions.html', context)
    else:
        if request.is_ajax():
            return render(request, 'login.html', {})
        return redirect('/?next=/subscriptions/')

def podinfo(request, itunesid):
    """
    returns a podinfo page
    ajax: episodes loaded separately via ajax
    non-ajax: episodes included + chart & search bar
    required argument: itunesid
    """

    if request.method == 'GET':
        user = request.user
        podcast = get_object_or_404(Podcast, itunesid=itunesid)
        podcast.set_subscribed(user)

        context = {
            'podcast': podcast,
        }

        if request.is_ajax():
            return render(request, 'podinfo.html', context)

        # chart & search bar
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts()
        episodes = podcast.get_episodes()
        episodes_count = len(episodes)

        if episodes_count == 1:
            episodes_header = str(episodes_count) + ' episode of ' + podcast.title
        else:
            episodes_header = str(episodes_count) + ' episodes of ' + podcast.title

        chart_header = 'Top 50 podcasts on iTunes'

        context.update({
            'chart_genres': genres,
            'chart': chart[:50],
            'alphabet': ALPHABET,
            'episodes': episodes,
            'episodes_header': episodes_header,
            'chart_header': chart_header,
        })
        return render(request, 'podinfo.html', context)

def settings(request):
    """
    GET returns settings form
    POST saves settings form, redirects to index
    with chart & search bar for non-ajax
    """

    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            context = {
                'user_form': UserForm(instance=request.user),
                'profile_form': ProfileForm(instance=request.user.profile),
            }

            if request.is_ajax():
                return render(request, 'settings.html', context)

            # chart & search bar
            genres = Genre.get_primary_genres()
            chart = Podcast.get_charts()
            chart_header = 'Top 50 podcasts on iTunes'

            context.update({
                'chart_genres': genres,
                'chart': chart[:50],
                'alphabet': ALPHABET,
                'chart_header': chart_header,
            })
            return render(request, 'settings.html', context)

        if request.method == 'POST':
            user_form = UserForm(instance=request.user, data=request.POST)
            profile_form = ProfileForm(instance=request.user.profile, data=request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                if request.is_ajax():
                    return render(request, 'settings.html', {})
                return redirect('/')
            else:
                context = {
                    'user_form': user_form,
                    'profile_form': profile_form,
                }

                if request.is_ajax():
                    return render(request, 'settings.html', context)

                # chart & search bar
                genres = Genre.get_primary_genres()
                chart = Podcast.get_charts()
                chart_header = 'Top 50 podcasts on iTunes'
                context.update({
                    'chart_genres': genres,
                    'chart': chart[:50],
                    'alphabet': ALPHABET,
                    'chart_header': chart_header,
                })
                return render(request, 'settings.html', context)
    else:
        if request.is_ajax():
            return render(request, 'login.html', {})
        return redirect('/?next=/settings/')
