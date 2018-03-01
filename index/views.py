from django.shortcuts import render, redirect, Http404, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from .forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast, Episode, Played_Episode, Playlist_Episode
from django.views.decorators.vary import vary_on_headers
from urllib.parse import urlencode
import json
import logging
from django.core.cache import cache
logger = logging.getLogger(__name__)

def cookie_test(session):
    if session.test_cookie_worked():
        session['cookie'] = True
        session.delete_test_cookie()
        return False
    else:
        session.set_test_cookie()
        return True

def dopebar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == 'GET':
        if request.is_ajax():
            return render(request, 'dopebar.html', {})

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

        if not request.session.get('cookie', None):
            context['cookie_banner'] = cookie_test(request.session)

        last_played = Played_Episode.get_last_played()
        charts = Podcast.get_charts()
        context.update({
            'charts': charts,
            'last_played': last_played,
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
        user = request.user
        genre = request.GET.get('genre', None)
        try:
            genre = Genre.objects.get(name=genre)
        except Genre.DoesNotExist:
            genre = None
        language = request.GET.get('language', None)
        try:
            language = Language.objects.get(name=language)
        except Language.DoesNotExist:
            language = None

        provider = request.GET.get('provider', None)
        providers = ['dopepod', 'itunes']
        if provider not in providers:
            provider = providers[0]

        charts = Podcast.get_charts(provider=provider, genre=genre, language=language)

        if request.is_ajax():
            context = {
                'results': charts,
            }

            return render(request, 'results_base.html', context)

        last_played = Played_Episode.get_last_played()
        context.update({
            'charts': charts,
            'last_played': last_played,
        })

        if user.is_authenticated:
            return render(request, 'dashboard.html', context)
        else:
            return render(request, 'splash.html', context)

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
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ#'
        languages = Language.objects.all()
        genres = Genre.get_primary_genres()

        q = request.GET.get('q', None)
        if q:
            q.strip()
            if len(q) > 30:
                q = q[:30]

        genre = request.GET.get('genre', None)
        if genre:
            try:
                genre = genres.get(name=genre)
            except Genre.DoesNotExist:
                genre = None

        language = request.GET.get('language', None)
        if language:
            try:
                language = languages.get(name=language)
            except Language.DoesNotExist:
                language = None

        view = request.GET.get('view', None)
        if not view:
            view = 'grid'

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        show = 100

        results = Podcast.search(q, genre, language, page, show, view, alphabet, genres, languages)

        context = {
            'results': results,
        }
        if request.is_ajax():
            return render(request, 'results_base.html', context)

        results['extend'] = True

        charts = Podcast.get_charts()
        last_played = Played_Episode.get_last_played()

        context.update({
            'charts': charts,
            'last_played': last_played,
        })

        return render(request, 'results_base.html', context)

@vary_on_headers('Accept')
def subscriptions(request):
    """
    returns subscriptions for user
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        subscriptions = Subscription.get_subscriptions(user)

        context = {
            'results': subscriptions,
        }
        if request.is_ajax():
            return render(request, 'results_base.html', context)

        subscriptions['extend'] = True

        charts = Podcast.get_charts()
        last_played = Played_Episode.get_last_played()
        context.update({
            'charts': charts,
            'last_played': last_played,
        })

        return render(request, 'results_base.html', context)

@vary_on_headers('Accept')
def playlist(request):
    if request.method == 'GET':
        user = request.user
        playlist = Playlist_Episode.get_playlist(user)

        context = {
            'results': playlist,
        }
        if request.is_ajax():
            return render(request, 'results_base.html', context)

        playlist['extend'] = True

        charts = Podcast.get_charts()
        last_played = Played_Episode.get_last_played()
        context.update({
            'charts': charts,
            'last_played': last_played,
        })

        return render(request, 'results_base.html', context)

@vary_on_headers('Accept')
def showpod(request, podid):
    """
    returns a showpod page
    ajax: episodes loaded separately via ajax
    non-ajax: episodes included + chart & search bar
    required argument: podid
    """

    if request.method == 'GET':
        user = request.user
        try:
            podcast = Podcast.objects.get(podid=podid)
            podcast.views += 1
            podcast.save()
            if user.is_authenticated:
                podcast.is_subscribed(user)

            context = {
                'podcast': podcast,
            }

            if request.is_ajax():
                return render(request, 'showpod.html', context)

            charts = Podcast.get_charts()
            episodes = Episode.get_episodes(podcast)
            episodes = Episode.set_new(user, podcast, episodes)
            results = {
                'episodes': episodes,
            }

            last_played = Played_Episode.get_last_played()
            context.update({
                'charts': charts,
                'results': results,
                'last_played': last_played,
            })

            return render(request, 'showpod.html', context)
        except Podcast.DoesNotExist:
            raise Http404

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

            charts = Podcast.get_charts()
            last_played = Played_Episode.get_last_played()
            context.update({
                'charts': charts,
                'last_played': last_played,
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
                    return render(request, 'dashboard.html', context)
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

                charts = Podcast.get_charts()
                last_played = Played_Episode.get_last_played()
                context.update({
                    'charts': charts,
                    'last_played': last_played,
                })

                return render(request, 'settings.html', context)
    else:
        if request.is_ajax():
            return render(request, 'splash.html', {})
        return redirect('/?next=/settings/')
