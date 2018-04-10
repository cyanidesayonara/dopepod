from django.shortcuts import render, redirect
from django.http import Http404
from .models import Podcast, Subscription, Episode
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

def episodes(request, podid):
    """
    returns html for episodes
    GET ajax request sent by showpod
    required argument: podid
    """

    # ajax using POST
    if request.method == "GET":
        if request.is_ajax():
            user = request.user
            try:
                podcast = Podcast.objects.get(podid=podid)
                podcast.is_subscribed(user)
            except Podcast.DoesNotExist:
                raise Http404

            # page
            page = request.GET.get("page", None)
            try:
                page = int(page)
            except (TypeError, ValueError):
                page = 1
            
            url = request.get_full_path()
            episodes = Episode.get_episodes(url, podcast.podid, podcast.feedUrl, page)
            
            results = {}

            for page in episodes:
                results.update(page)
            Episode.set_new(user, podcast.podid, results["episodes"])

            context = {
                "results": results,
            }
            return render(request, "episodes.min.html", context)
        else:
            return redirect("/showpod/" + podid + "/")

def last_played(request):
    """
    returns n number of last played
    """

    if request.method == "GET":
        if request.is_ajax():
            last_played = Episode.get_last_played()
            context = {
                "results": last_played,
            }
            return render(request, "results_base.min.html", context)
        else:
            return redirect("/")
