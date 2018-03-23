from django.shortcuts import render, redirect
from django.http import Http404
from .models import Podcast, Subscription, Episode
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.template.loader import render_to_string

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
            results = Episode.get_episodes(podid)
            Episode.set_new(user, podid, results['episodes'])
            context = {
                'results': results,
            }
            return JsonResponse({
                "payload": render_to_string('episodes.min.html', context, request=request),
            })
        else:
            return redirect('/showpod/' + podid + '/')

def last_played(request):
    """
    returns n number of last played
    """
    # TODO update only new episodes
    if request.method == 'GET':
        if request.is_ajax():
            last_seen = get_last_seen(request.session)
            last_played, last_played_latest = Episode.get_last_played(last_seen)
            context = {
                'results': last_played_latest,
            }
            return JsonResponse({
                "payload": render_to_string('results_base.min.html', context, request=request),
            })
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
                podid = int(request.POST['podid'])
                podcast = Podcast.objects.get(podid=podid)
                podcast.subscribe_or_unsubscribe(user)
                podcast.is_subscribed(user)
            except (ValueError, KeyError, Podcast.DoesNotExist):
                raise Http404()

            context = {
                'podcast': podcast,
            }

            if request.is_ajax():
                return JsonResponse({
                    "payload": render_to_string('showpod.min.html', context, request=request),
                })
            return redirect('/showpod/' + str(podid) + '/')
        else:
            if request.is_ajax():
                return JsonResponse({
                    "payload": render_to_string('splash.min.html', {}, request=request),
                })
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
            except (ValueError, KeyError, Podcast.DoesNotExist):
                raise Http404()

            results = Subscription.get_subscriptions(user)
            context = {
                'results': results,
            }
            return JsonResponse({
                "payload": render_to_string('showpod.min.html', context, request=request),
            })
        else:
            return JsonResponse({
                "payload": render_to_string('splash.min.html', {}, request=request),
            })
