from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from .models import Genre, Language, Podcast, Subscription, Episode
import logging
import requests

logger = logging.getLogger(__name__)

def episodes(request):
    """
    returns html for episodes
    POST ajax request sent by podinfo
    required argument: itunesid
    """

    # ajax using POST
    if request.method == 'POST':
        try:
            itunesid = request.POST['itunesid']
            podcast = Podcast.objects.get(itunesid=int(itunesid))
        except (KeyError, Podcast.DoesNotExist) as e:
            raise Http404()

        context = {
            'podcast': podcast,
        }

        context = Episode.get_episodes(context, podcast, ajax=True)

        return render(request, 'results_base.html', context)

def play(request):
    """
    returns html5 audio element
    POST request in a popup
    POST ajax request, in multibar (#player)
    """

    # TODO: itemize episode, get url after redirections
    if request.method == 'POST':
        episode = {}
        try:
            episode['url'] = request.POST['url']
            episode['kind'] = request.POST['type']
            episode['title'] = request.POST['title']
            episode['date'] = request.POST['date']
            episode['itunesid'] = request.POST['itunesid']
            episode['podcast'] = Podcast.objects.get(itunesid=episode['itunesid'])

            player = {
                'episode': episode,
            }

            context = {
                'player': player,
            }

            return render(request, 'player.html', context)
        except KeyError:
            raise Http404()

def subscribe(request):
    """
    subscribe to podcast via POST request
    delete existing subscription or create a new one
    ajax update subscribers with correct value
    non-ajax redirects to current page
    if not logged in, redirects to login
    """

    # validate request
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            try:
                itunesid = request.POST['itunesid']
                podcast = Podcast.objects.get(itunesid=int(itunesid))
            except (KeyError, Podcast.DoesNotExist) as e:
                raise Http404()

            podcast.subscribe(user)
            podcast.set_subscribed(user)

            context = {
                'podcast': podcast,
            }

            if request.is_ajax():
                return render(request, 'podinfo.html', context)
            return redirect('/podinfo/' + itunesid + '/')

        else:
            if request.is_ajax():
                return render(request, 'splash.html', {})
            return redirect('/?next=/podinfo/' + itunesid + '/')
