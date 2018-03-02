from django.shortcuts import render, redirect
from django.http import Http404
from .models import Podcast, Subscription, Episode
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def episodes(request, podid):
    """
    returns html for episodes
    GET ajax request sent by showpod
    required argument: podid
    """

    # ajax using POST
    if request.method == 'GET':
        if request.is_ajax():
            user = request.user
            try:
                podcast = Podcast.objects.get(podid=podid)
            except Podcast.DoesNotExist:
                raise Http404()

            episodes = Episode.get_episodes(podcast)
            episodes = Episode.set_new(user, podcast, episodes)
            results = {
                'episodes': episodes,
            }
            context = {
                'results': results,
            }
            return render(request, 'episodes.html', context)
        else:
            return redirect('/showpod/' + podid + '/')

def last_played(request):
    """
    returns n number of last played
    """
    # TODO update only new episodes
    if request.method == 'GET':
        if request.is_ajax():
            last_played = Episode.get_last_played()
            context = {
                'results': last_played,
            }
            return render(request, 'results_base.html', context)
        else:
            return redirect('/')

def subscribe(request):
    """
    subscribe to podcast via POST request
    delete existing subscription or create a new one
    ajax update subscribers with correct value
    non-ajax redirects to current page
    if not logged in, redirects to login
    """

    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            try:
                podid = request.POST['podid']
                podcast = Podcast.objects.get(podid=int(podid))
                podcast.subscribe_or_unsubscribe(user)
                podcast.is_subscribed(user)
            except (ValueError, KeyError, Podcast.DoesNotExist) as e:
                raise Http404()

            context = {
                'podcast': podcast,
            }

            if request.is_ajax():
                return render(request, 'showpod.html', context)
            return redirect('/showpod/' + podid + '/')

        else:
            if request.is_ajax():
                return render(request, 'splash.html', {})
            return redirect('/?next=/showpod/' + podid + '/')

def unsubscribe(request):
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
                podids = request.POST.getlist('podids[]')
                for podid in podids:
                    podcast = Podcast.objects.get(podid=int(podid))
                    podcast.unsubscribe(user)
            except (ValueError, KeyError, Podcast.DoesNotExist) as e:
                raise Http404()

            subscriptions = Subscription.get_subscriptions(user)

            context = {
                'results': subscriptions,
            }
            return render(request, 'results_base.html', context)

        else:
            return render(request, 'splash.html', {})
