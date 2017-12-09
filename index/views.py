from django.shortcuts import render, redirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests


ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '#']

def navbar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == 'GET':
        return render(request, 'navbar.html', {})

def index(request):
    if request.method == 'GET':
        context = {
        'alphabet': ALPHABET,
        'selected_alphabet': 'A',
        'search': True,
        }

        if not request.is_ajax():
            user = request.user
            genres = Genre.get_primary_genres()
            chart = Podcast.get_charts(user)
            context['results_info'] = 'top podcasts in All'
            context['genres'] = genres
            context['chart'] = chart

        return render(request, 'index/index.html', context)

def charts(request):
    if request.method == 'GET':
        genre = request.GET.get('genre', None)
        user = request.user
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts(user, genre)
        results_info = 'top podcasts in ' + ('All' if genre == None else genre)

        context = {
            'chart': chart,
            'genres': genres,
            'selected_genre': genre,
            'results_info': results_info,
        }

        if not request.is_ajax():
            context['alphabet'] = ALPHABET
            context['selected_alphabet'] = 'A'
            context['search'] = True
            return render(request, 'index/index.html', context)
        return render(request, 'index/charts.html', context)

def search(request):
    """
    set search terms
    """

    if request.method == 'GET':

        q = request.GET.get('q', None)

        # if query string, return results
        if q:
            user = request.user

            genre = request.GET.get('genre', None)
            language = request.GET.get('language', None)
            is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
            explicit = is_true(request.GET.get('explicit', 'true'))
            page = int(request.GET.get('page', '1'))
            languages = Language.objects.all()
            genres = Genre.get_primary_genres()

            # return podcasts matching search terms
            podcasts = Podcast.search(genre, language, explicit, user, q=q)

            results_info = str(podcasts.count()) + ' results for "' + q + '"'

            context = {
                'genres': genres,
                'languages': languages,
                'selected_q': q,
                'selected_genre': genre,
                'selected_language': language,
                'results_info': results_info,
                'search': True,
            }

            if not request.is_ajax():
                context['chart'] = Podcast.get_charts(user)
                context['alphabet'] = ALPHABET

            paginator = Paginator(podcasts, 24)

            try:
                podcasts = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                podcasts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                podcasts = paginator.page(paginator.num_pages)

            if user.is_authenticated:
                for podcast in podcasts:
                    podcast.set_subscribed(user)

            context['podcasts'] = podcasts
            return render(request, 'index/results_detail.html', context)

        else:
            if request.is_ajax():
                return render(request, 'index/results_detail.html', {})
            return redirect('index')

def browse(request):
    """
    set browse terms
    """

    user = request.user

    if request.method == 'GET':
        alphabet = request.GET.get('alphabet', 'A')
        languages = Language.objects.all()
        genre = request.GET.get('genre', None)
        language = request.GET.get('language', None)
        page = int(request.GET.get('page', '1'))
        is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
        explicit = is_true(request.GET.get('explicit', 'true'))
        genres = Genre.get_primary_genres()

        podcasts = Podcast.search(genre, language, explicit, user, alphabet=alphabet)

        results_info = str(podcasts.count()) + ' results for "' + alphabet + '"'

        context = {
            'genres': genres,
            'languages': languages,
            'selected_alphabet': alphabet,
            'selected_genre': genre,
            'selected_language': language,
            'results_info': results_info,
            'browse': True,
        }

        if not request.is_ajax():
            context['chart'] = Podcast.get_charts(user)
            context['alphabet'] = ALPHABET

        paginator = Paginator(podcasts, 120)


        try:
            podcasts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            podcasts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            podcasts = paginator.page(paginator.num_pages)

        context['podcasts'] = podcasts
        context['podcasts1'] = podcasts[:40]
        context['podcasts2'] = podcasts[40:80]
        context['podcasts3'] = podcasts[80:120]

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
            subscriptions = Subscription.get_subscriptions(user)
            results_info = str(subscriptions.count()) + ' subscriptions'

            context = {
                'results_info': results_info,
                'subscriptions': subscriptions,
                'search': True
            }

            if not request.is_ajax():
                genres = Genre.get_primary_genres()
                chart = Podcast.get_charts(user)
                context['genres'] = genres
                context['chart'] = chart
                context['alphabet'] = ALPHABET
                context['selected_alphabet'] = 'A'
            return render(request, 'index/subscriptions.html', context)
    else:
        raise Http404()

def podinfo(request, itunesid):
    """
    returns a podinfo page
    ajax: episodes loaded separately via ajax
    non-ajax: episodes included
    required argument: itunesid
    """

    if request.method == 'GET':
        user = request.user
        podcast = get_object_or_404(Podcast, itunesid=itunesid)

        if user.is_authenticated:
            podcast.set_subscribed(user)
        context = {
            'podcast': podcast,
        }

        if not request.is_ajax():
            genres = Genre.get_primary_genres()
            chart = Podcast.get_charts(user)
            context['genres'] = genres
            context['chart'] = chart
            context['alphabet'] = ALPHABET
            context['selected_alphabet'] = 'A'
            context['search'] = True
            context['episodes'] = podcast.get_episodes()
        return render(request, 'podinfo.html', context)

def settings(request):
    """
    GET return settings form
    POST save settings form
    """
    user = request.user
    if user.is_authenticated:
        context = {
            'search': True
        }
        if not request.is_ajax():
            genres = Genre.get_primary_genres()
            chart = Podcast.get_charts(user)
            context['genres'] = genres
            context['chart'] = chart
            context['alphabet'] = ALPHABET
            context['selected_alphabet'] = 'A'

        if request.method == 'GET':
            context['user_form'] = UserForm(instance=request.user)
            context['profile_form'] = ProfileForm(instance=request.user.profile)
            return render(request, 'index/settings.html', context)

        if request.method == 'POST':
            user_form = UserForm(instance=request.user)
            profile_form = ProfileForm(instance=request.user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                return redirect('/')
            else:
                context['user_form'] = user_form
                context['profile_form'] = profile_form
                return render(request, 'index/settings.html', context)
    else:
        raise Http404()
