from django.shortcuts import render, redirect, Http404, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from .forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Chart, Subscription, Podcast, Episode
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

        context = Chart.get_charts(context)

        context.update({
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
        user = request.user
        genres = Genre.get_primary_genres()

        genre = request.GET.get('genre', None)
        if genre:
            if genre not in genres.values_list('name', flat=True):
                genre = None

        context = {}
        if request.is_ajax():
            context = Chart.get_charts(context, genre, ajax=True)
            return render(request, 'results_base.html', context)

        context = Chart.get_charts(context, genre)
        context = {
            'alphabet': ALPHABET,
        }

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
        languages = Language.objects.all()
        genres = Genre.get_primary_genres()
        q = request.GET.get('q', None)

        view = 'list'
        show = 160

        if q:
            q.strip()
            if len(q) > 30:
                q = None
            elif len(q) > 1:
                view = 'grid'
                show = 60

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

        results = {}
        results['drop'] = 'search'
        results['podcasts'] = podcasts
        if view == 'list':
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

        if request.is_ajax():
            context = {
            'results': results,
            }
            return render(request, 'results_base.html', context)

        context = {}
        context = Chart.get_charts(context)

        context.update({
            'search': results,
            'alphabet': ALPHABET,
        })

        if user.is_authenticated:
            return render(request, 'dashboard.html', context)
        else:
            return render(request, 'splash.html', context)

@vary_on_headers('Accept')
def subscriptions(request):
    """
    returns subscriptions for user
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        subscriptions = user.subscription_set.all()

        if subscriptions.count() == 1:
            results_header = str(subscriptions.count()) + ' subscriptions'
        else:
            results_header = str(subscriptions.count()) + ' subscriptions'

        results = {}
        results['drop'] = 'search'
        results['podcasts'] = subscriptions
        results['header'] = results_header
        results['view'] = 'subscriptions'
        results['extra_options'] = True


        if request.is_ajax():
            context = {
            'results': results,
            }
            return render(request, 'results_base.html', context)

        context = {
            'search': results,
        }
        context = Chart.get_charts(context)

        if user.is_authenticated:
            return render(request, 'dashboard.html', context)
        else:
            return render(request, 'splash.html', context)

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
        try:
            podcast = Podcast.objects.get(itunesid=itunesid)
            podcast.set_subscribed(user)
            podcast.views += 1
            podcast.save()

            context = {
                'podcast': podcast,
            }

            if request.is_ajax():
                return render(request, 'podinfo.html', context)

            context = Episode.get_episodes(context, podcast)

            context = Chart.get_charts(context)

            context.update({
                'alphabet': ALPHABET,
            })
            return render(request, 'podinfo.html', context)
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

            context = Chart.get_charts(context)

            context.update({
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

                context = Chart.get_charts(context)

                context.update({
                    'alphabet': ALPHABET,
                })
                return render(request, 'settings.html', context)
    else:
        if request.is_ajax():
            return render(request, 'splash.html', {})
        return redirect('/?next=/settings/')
