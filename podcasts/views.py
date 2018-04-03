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
    if request.method == "GET":
        if request.is_ajax():
            user = request.user

            # page
            page = request.GET.get("page", None)
            try:
                page = int(page)
            except (TypeError, ValueError):
                page = 1
            
            url = request.get_full_path()
            episodes = Episode.get_episodes(url, podid, page)
            
            results = {}

            for page in episodes:
                results.update(page)
            Episode.set_new(user, podid, results["episodes"])
            results["podcast"].is_subscribed(user)

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
