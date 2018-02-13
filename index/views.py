from django.shortcuts import render, redirect, Http404, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from .forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Chart, Subscription, Podcast, Episode, Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.vary import vary_on_headers
from urllib.parse import urlencode
import json

def dopebar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == 'GET':
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

        last_played = Episode.get_last_played()
        charts = Chart.get_charts()
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

        providers = ['dopepod', 'itunes']
        provider = request.GET.get('provider', None)
        if provider not in providers:
            provider = providers[0]

        charts = Chart.get_charts(genre=genre, provider=provider)

        if request.is_ajax():
            context = {
                'results': charts,
            }

            return render(request, 'results_base.html', context)

        last_played = Episode.get_last_played()
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
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0'
        user = request.user
        languages = Language.objects.all()
        genres = Genre.get_primary_genres()
        view = request.GET.get('view', None)
        q = request.GET.get('q', None)

        if not view:
            if q and len(q) > 1:
                view = 'grid'
            else:
                view = 'list'

        show = 100

        if q:
            if q == '0':
                q = '#'
            q.strip()
            if len(q) > 30:
                q = None

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

        podcount, podcasts = Podcast.search(user, genre, language, q, show)
        pagecount = podcount / show

        if not q:
            results_header = str(podcount) + ' podcasts'
        elif pagecount == 1:
            results_header = str(podcount) + ' result for "' + q + '"'
        else:
            results_header = str(podcount) + ' results for "' + q + '"'

        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        url = request.path
        querystring = {}
        urls = {}

        if q:
            querystring['q'] = q
        if genre:
            querystring['genre'] = genre
        if language:
            querystring['language'] = language
        if view:
            querystring['view'] = view

        if q or genre or language:
            querystring_wo_q = {x: querystring[x] for x in querystring if x not in {'q'}}
            urls['q_url'] = url + '?' + urlencode(querystring_wo_q)

            querystring_wo_genre = {x: querystring[x] for x in querystring if x not in {'genre'}}
            urls['genre_url'] = url + '?' + urlencode(querystring_wo_genre)

            querystring_wo_language = {x: querystring[x] for x in querystring if x not in {'language'}}
            urls['language_url'] = url + '?' + urlencode(querystring_wo_language)

            urls['full_url'] = url + '?' + urlencode(querystring)
        else:
            urls['q_url'] = url + '?'
            urls['genre_url'] = url + '?'
            urls['language_url'] = url + '?'
            urls['full_url'] = url + '?'

        results = {}
        if pagecount > 1:
            pages = range((page - 2 if page - 2 > 1 else 1), (page + 2 if page + 2 <= pagecount else pagecount) + 1)
            results['pagination'] = {
                'start': True if page != 1 else False,
                'pages': pages,
                'page': page,
                'end': True if page != pagecount else False,
            }
        results['alphabet'] = alphabet
        results['podcasts'] = podcasts
        one = show // 4
        two = show // 2
        three = show // 2 + show // 4
        results['podcasts1'] = podcasts[:one]
        results['podcasts2'] = podcasts[one:two]
        results['podcasts3'] = podcasts[two:three]
        results['podcasts4'] = podcasts[three:]

        results['header'] = results_header
        results['selected_q'] = q
        results['selected_genre'] = genre
        results['selected_language'] = language
        results['genres'] = genres
        results['languages'] = languages
        results['view'] = view
        results['urls'] = urls
        results['extra_options'] = True

        context = {
            'results': results,
        }
        if request.is_ajax():
            return render(request, 'results_base.html', context)

        results['extend'] = True

        charts = Chart.get_charts()
        last_played = Episode.get_last_played()

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
        subscriptions = Subscription.objects.filter(user=user)

        if subscriptions.count() == 1:
            results_header = str(subscriptions.count()) + ' subscription'
        else:
            results_header = str(subscriptions.count()) + ' subscriptions'

        results = {}
        results['podcasts'] = subscriptions
        results['header'] = results_header
        results['view'] = 'subscriptions'
        results['extra_options'] = True

        context = {
            'results': results,
        }
        if request.is_ajax():
            return render(request, 'results_base.html', context)

        results['extend'] = True

        charts = Chart.get_charts()
        last_played = Episode.get_last_played()
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
                podcast.set_subscribed(user)

            podcast.get_ranks()

            context = {
                'podcast': podcast,
            }

            if request.is_ajax():
                return render(request, 'showpod.html', context)

            charts = Chart.get_charts()
            episodes = Episode.get_episodes(podcast)
            last_played = Episode.get_last_played()
            context.update({
                'charts': charts,
                'episodes': episodes,
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

            charts = Chart.get_charts()
            last_played = Episode.get_last_played()
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

                charts = Chart.get_charts()
                last_played = Episode.get_last_played()
                context.update({
                    'charts': charts,
                    'last_played': last_played,
                })

                return render(request, 'settings.html', context)
    else:
        if request.is_ajax():
            return render(request, 'splash.html', {})
        return redirect('/?next=/settings/')
