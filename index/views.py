from django.shortcuts import render, redirect, Http404, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast, Episode
from django.views.decorators.vary import vary_on_headers
from urllib.parse import urlencode
from django.db.models import F
import json
import logging
from django.core.cache import cache
from django.template.loader import render_to_string
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
            return JsonResponse({
                "payload": render_to_string('dopebar.min.html', {}, request=request),
            })

@vary_on_headers('Accept')
def index(request):
    """
    returns index page
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        view = request.GET.get('view' , None)

        if user.is_authenticated:
            template = 'dashboard.min.html'
        else:
            template = 'splash.min.html'
        context = {
            'view': view,
        }
        last_played = Episode.get_last_played()
        url = request.get_full_path()
        charts = Podcast.search(url=url, provider='dopepod')

        if request.is_ajax():
            return JsonResponse({
                "payload": render_to_string(template, context, request=request),
                # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
            })

        context.update({
            'charts': charts,
            'last_played': last_played,
        })
        if not request.session.get('cookie', None):
            context['cookie_banner'] = cookie_test(request.session)

        return render(request, template, context)

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

        url = request.get_full_path()
        results = Podcast.search(
            url=url, provider=provider, genre=genre, language=language
        )

        last_played = Episode.get_last_played()
        context = {
            'results': results,
        }

        if request.is_ajax():
            return JsonResponse({
                "payload": render_to_string("results_base.min.html", context, request=request),
                "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
            })

        context = {
            'charts': results,
            'last_played': last_played,
        }

        if user.is_authenticated:
            return render(request, 'dashboard.min.html', context)
        else:
            return render(request, 'splash.min.html', context)

@vary_on_headers('Accept')
def search(request):
    """
    sets search terms
    calls search
    returns results
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        
        # get q
        q = request.GET.get('q', None)
        if q:
            q = q.strip().lower()
            if len(q) > 30:
                q = q[:30]

        # get genre
        genre = request.GET.get('genre', None)
        if genre:
            try:
                genre = Genre.objects.get(name=genre)
            except Genre.DoesNotExist:
                genre = None

        # get lang
        language = request.GET.get('language', None)
        if language:
            try:
                language = Language.objects.get(name=language)
            except Language.DoesNotExist:
                language = None

        # get view
        view = request.GET.get('view', None)
     
        # page
        page = request.GET.get('page', None)
        if page:
            try:
                page = int(page)
            except ValueError:
                page = 1

        # get show
        show = None

        # get url
        url = request.get_full_path()

        results = Podcast.search(
            url=url, q=q, genre=genre, language=language, show=show, page=page, view=view
        )
        charts = Podcast.search(url=url, provider='dopepod')
        last_played = Episode.get_last_played()

        if request.is_ajax():
            return JsonResponse({
                "payload": render_to_string("results_base.min.html", {'results': results}, request=request),
                # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
            })

        results['extend'] = True

        context = {
            'results': results,
            'charts': charts,
            'last_played': last_played,
        }
        return render(request, 'results_base.min.html', context)

@vary_on_headers('Accept')
def subscriptions(request):
    """
    returns subscriptions for user
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        if user.is_authenticated:
            results = Subscription.get_subscriptions(user)
            url = request.get_full_path()
            charts = Podcast.search(url=url, provider='dopepod')
            last_played = Episode.get_last_played()

            if request.is_ajax():
                return JsonResponse({
                    "payload": render_to_string("results_base.min.html", {'results': results}, request=request),
                    # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                    "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
                })

            results['extend'] = True

            context = {
                'results': results,
                'charts': charts,
                'last_played': last_played,
            }

            return render(request, 'results_base.min.html', context)
        else:
            if request.is_ajax():
                url = request.get_full_path()
                charts = Podcast.search(url=url, provider='dopepod')
                last_played = Episode.get_last_played()
                return JsonResponse({
                    "payload": render_to_string('splash.min.html', {}, request=request),
                    # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                    "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
                })
            return redirect('/')

@vary_on_headers('Accept')
def playlist(request):
    if request.method == 'GET':
        user = request.user
        if user.is_authenticated:
            results = Episode.get_playlist(user)
            url = request.get_full_path()
            charts = Podcast.search(url=url, provider='dopepod')
            last_played = Episode.get_last_played()

            if request.is_ajax():
                return JsonResponse({
                    "payload": render_to_string("results_base.min.html", {'results': results}, request=request),
                    # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                    "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
                })

            results['extend'] = True

            context = {
                'results': results,
                'charts': charts,
                'last_played': last_played,
            }
            return render(request, 'results_base.min.html', context)
        else:
            if request.is_ajax():
                url = request.get_full_path()
                charts = Podcast.search(url=url, provider='dopepod')
                last_played = Episode.get_last_played()
                return JsonResponse({
                    "payload": render_to_string('splash.min.html', {}, request=request),
                    # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                    "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
                })
            return redirect('/')

    if request.method == 'POST':
        user = request.user
        try:
            mode = request.POST['mode']
            if mode == 'play':
                # returns html5 audio element
                # POST request in a popup
                # POST ajax request

                try:
                    signature = request.POST['signature']
                    episode = Episode.add(signature, user)
                except KeyError:
                    try:
                        position = int(request.POST['pos']) + 1
                        episode = Episode.objects.get(user=user, position=position)
                    except (KeyError, Episode.DoesNotExist):
                        raise Http404()

                episode.play()
                context = {
                    'episode': episode,
                }
                return JsonResponse({
                    "payload": render_to_string('player.min.html', context, request=request),
                })
            if user.is_authenticated:
                if mode == 'add':
                    signature = request.POST['signature']
                    Episode.add(signature, user)
                elif mode == 'remove':
                    pos = int(request.POST['pos'])
                    Episode.remove(pos, user)
                elif mode == 'up':
                    pos = int(request.POST['pos'])
                    Episode.up(pos, user)
                elif mode == 'down':
                    pos = int(request.POST['pos'])
                    Episode.down(pos, user)
                else:
                    raise Http404()
            else:
                raise Http404()
        except (KeyError, TypeError):
            raise Http404()

        results = Episode.get_playlist(user)
        url = request.get_full_path()
        charts = Podcast.search(url=url, provider='dopepod')
        last_played = Episode.get_last_played()
        if request.is_ajax():
            return JsonResponse({
                "payload": render_to_string("results_base.min.html", {'results': results}, request=request),
                # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
            })

        results['extend'] = True

        context = {
            'results': results,
            'charts': charts,
            'last_played': last_played,
        }
        return render(request, 'results_base.min.html', context)

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
            podcast.views = F('views') + 1
            podcast.save()
            podcast.is_subscribed(user)

            url = request.get_full_path()
            charts = Podcast.search(url=url, provider='dopepod')
            last_played = Episode.get_last_played()

            if request.is_ajax():
                return JsonResponse({
                    "payload": render_to_string("showpod.min.html", {'podcast': podcast}, request=request),
                    # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                    "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
                })

            results = Episode.get_episodes(podid)
            Episode.set_new(user, podid, results['episodes'])
            context = {
                'podcast': podcast,
                'charts': charts,
                'results': results,
                'last_played': last_played,
            }

            return render(request, 'showpod.min.html', context)
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
        results = {
            'header': 'Settings',
            'view': 'settings',
            'extra_options': True,
        }
        if request.method == 'GET':
            context = {
                'results': results,
                'user_form': UserForm(instance=request.user),
                'profile_form': ProfileForm(instance=request.user.profile),
            }
            url = request.get_full_path()
            charts = Podcast.search(url=url, provider='dopepod')
            last_played = Episode.get_last_played()

            if request.is_ajax():
                return JsonResponse({
                    "payload": render_to_string("results_base.min.html", {'context': context}, request=request),
                    # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                    "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
                })

            results['extend'] = True

            context.update({
                'charts': charts,
                'last_played': last_played,
            })

            return render(request, 'results_base.min.html', context)

        if request.method == 'POST':
            user_form = UserForm(instance=request.user, data=request.POST)
            profile_form = ProfileForm(instance=request.user.profile, data=request.POST)

            context = {
                'results': results,
                'user_form': user_form,
                'profile_form': profile_form,
            }

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                if request.is_ajax():
                    return JsonResponse({
                        "payload": render_to_string("dashboard.min.html", {}, request=request),
                        # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                        "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
                    })
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
                url = request.get_full_path()
                charts = Podcast.search(url=url, provider='dopepod')
                last_played = Episode.get_last_played()

                if request.is_ajax:
                    return JsonResponse({
                        "payload": render_to_string('results_base.min.html', context, request=request),
                        # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                        "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
                    }, status=400)

                results['extend'] = True

                context.update({
                    'charts': charts,
                    'last_played': last_played,
                })
                return render(request, 'results_base.min.html', context)
    else:
        if request.is_ajax():
            url = request.get_full_path()
            charts = Podcast.search(url=url, provider='dopepod')
            last_played = Episode.get_last_played()
            return JsonResponse({
                "payload": render_to_string('splash.min.html', {}, request=request),
                # "charts": render_to_string("results_base.min.html", {'results': charts}, request=request),
                "last_played": render_to_string("results_base.min.html", {'results': last_played}, request=request),
            })
        return redirect('/?next=/settings/')
