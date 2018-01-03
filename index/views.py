from django.shortcuts import render, redirect, Http404, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from .forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Chart, Subscription, Podcast
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.vary import vary_on_headers
import urllib.parse
import json

ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','#']

def navbar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == 'GET':
        return render(request, 'navbar.html', {})

@vary_on_headers('Accept')
def index(request):
    """
    returns index page
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        view = request.GET.get('view' , None)

        context = {
            'view': view,
        }

        if request.is_ajax():
            if user.is_authenticated:
                return render(request, 'dashboard.html', context)
            else:
                return render(request, 'splash.html', context)

        # chart and search bar for non-ajax
        chart = Chart.objects.get(genre=None)
        genres = Genre.get_primary_genres()

        context.update({
            'splash': True,
            'chart': chart,
            'chart_genres': genres,
            'alphabet': ALPHABET,
        })

        if user.is_authenticated:
            return render(request, 'dashboard.html', context)
        else:
            return render(request, 'splash.html', context)

@vary_on_headers('Accept')
def charts(request):
    """
    returns chart (optional: for requested genre)
    with search bar for non-ajax
    """

    if request.method == 'GET':
        genres = Genre.get_primary_genres()

        genre = request.GET.get('genre', None)
        if genre:
            if genre not in genres.values_list('name', flat=True):
                genre = None
        chart = Chart.objects.get(genre=genre)

        context = {
            'chart': chart,
            'chart_genres': genres,
        }

        if request.is_ajax():
            return render(request, 'charts.html', context)

        # search bar + subs for non-ajax
        context.update({
            'alphabet': ALPHABET,
        })

        return render(request, 'base.html', context)

@vary_on_headers('Accept')
def search(request):
    """
    sets search terms
    calls search
    returns results
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        languages = Language.objects.all()
        genres = Genre.get_primary_genres()
        q = request.GET.get('q', None)

        view = 'list'
        show = 160
        template = 'results_list.html'

        if q:
            q.strip()
            if len(q) > 30:
                q = None
            elif len(q) > 1:
                view = 'detail'
                show = 60
                template = 'results_detail.html'

        genre = request.GET.get('genre', None)
        if genre and genre not in genres.values_list('name', flat=True):
            genre = None

        language = request.GET.get('language', None)
        if language and language not in languages.values_list('name', flat=True):
            language = None

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        podcasts = Podcast.search(genre, language, user, q=q)
        paginator = Paginator(podcasts, show)

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

        url = request.path
        querystring = {}
        urls = {}

        if q:
            querystring['q'] = q
        if genre:
            querystring['genre'] = genre
        if language:
            querystring['language'] = language

        if q or genre or language:
            querystring_wo_q = {x: querystring[x] for x in querystring if x not in {'q'}}
            urls['q_url'] = url + '?' + urllib.parse.urlencode(querystring_wo_q)

            querystring_wo_genre = {x: querystring[x] for x in querystring if x not in {'genre'}}
            urls['genre_url'] = url + '?' + urllib.parse.urlencode(querystring_wo_genre)

            querystring_wo_language = {x: querystring[x] for x in querystring if x not in {'language'}}
            urls['language_url'] = url + '?' + urllib.parse.urlencode(querystring_wo_language)

            urls['full_url'] = url + '?' + urllib.parse.urlencode(querystring)
        else:
            urls['q_url'] = url + '?'
            urls['genre_url'] = url + '?'
            urls['language_url'] = url + '?'
            urls['full_url'] = url + '?'

        context = {
            'urls': urls,
            'genres': genres,
            'languages': languages,
            'selected_q': q,
            'selected_genre': genre,
            'selected_language': language,
            'results_header': results_header,
            'podcasts': podcasts,
            'podcasts1': podcasts[:40],
            'podcasts2': podcasts[40:80],
            'podcasts3': podcasts[80:120],
            'podcasts4': podcasts[120:160],
        }

        if request.is_ajax():
            return render(request, template, context)

        chart = Chart.objects.get(genre=None)

        context.update({
            'chart_genres': genres,
            'chart': chart,
            'alphabet': ALPHABET,
        })

        return render(request, template, context)

@vary_on_headers('Accept')
def subscriptions(request):
    """
    returns subscriptions for user
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        podcasts = user.subscription_set.all()

        if podcasts.count() == 1:
            results_header = str(podcasts.count()) + ' subscriptions'
        else:
            results_header = str(podcasts.count()) + ' subscriptions'

        context = {
            'results_header': results_header,
            'podcasts': podcasts,
        }

        if request.is_ajax():
            return render(request, 'subscriptions.html', context)

        # chart & search bar for non-ajax
        genres = Genre.get_primary_genres()
        chart = Chart.objects.get(genre=None)

        context.update({
            'splash': True,
            'chart_genres': genres,
            'chart': chart,
            'alphabet': ALPHABET,
        })
        return render(request, 'subscriptions.html', context)
    else:
        if request.is_ajax():
            return render(request, 'splash.html', {})
        return redirect('/?next=/subscriptions/')

@vary_on_headers('Accept')
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
        podcast.views += 1
        podcast.save()

        context = {
            'podcast': podcast,
        }

        if request.is_ajax():
            return render(request, 'podinfo.html', context)

        # chart & search bar
        genres = Genre.get_primary_genres()
        episodes = podcast.get_episodes()
        episodes_count = len(episodes)

        if episodes_count == 1:
            episodes_header = str(episodes_count) + ' episode of ' + podcast.title
        else:
            episodes_header = str(episodes_count) + ' episodes of ' + podcast.title

        chart = Chart.objects.get(genre=None)

        context.update({
            'chart_genres': genres,
            'chart': chart,
            'alphabet': ALPHABET,
            'episodes': episodes,
            'episodes_header': episodes_header,
        })
        return render(request, 'podinfo.html', context)

@vary_on_headers('Accept')
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
            chart = Chart.objects.get(genre=None)

            context.update({
                'chart_genres': genres,
                'chart': chart,
                'alphabet': ALPHABET,
            })
            return render(request, 'settings.html', context)

        if request.method == 'POST':
            user_form = UserForm(instance=request.user, data=request.POST)
            profile_form = ProfileForm(instance=request.user.profile, data=request.POST)

            context = {
                'user_form': user_form,
                'profile_form': profile_form,
            }

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                if request.is_ajax():
                    return render(request, 'settings.html', context)
                return redirect('/')
            else:
                errors = {}

                data = json.loads(user_form.errors.as_json())
                keys = data.keys()
                for key in keys:
                    message = data[key][0]['message']
                    if message:
                        errors[key] = message

                data = json.loads(profile_form.errors.as_json())
                keys = data.keys()
                for key in keys:
                    message = data[key][0]['message']
                    if message:
                        errors[key] = message

                context.update({
                    'errors': errors,
                })

                if request.is_ajax:
                    return render(request, 'settings.html', context, status=400)

                # chart & search bar
                genres = Genre.get_primary_genres()
                chart = Chart.objects.get(genre=None)

                context.update({
                    'chart_genres': genres,
                    'chart': chart,
                    'alphabet': ALPHABET,
                })
                return render(request, 'settings.html', context)
    else:
        if request.is_ajax():
            return render(request, 'splash.html', {})
        return redirect('/?next=/settings/')
