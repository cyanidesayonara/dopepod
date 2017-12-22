from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from .models import Genre, Language, Podcast, Subscription
import logging
import requests

logger = logging.getLogger(__name__)

def dashboard(request):
    user = request.user
    if user.is_authenticated:
        subscriptions = Subscription.get_subscriptions(user)
        context = {
            'subscriptions': subscriptions,
        }
        return render(request, 'dashboard.html', context)
    else:
        signup = request.POST.get('signup' , None)
        context = {
            'signup': signup,
        }
        return render(request, 'login_signup.html', context)

def episodes(request):
    """
    returns html for episodes
    POST ajax request sent from podinfo
    required argument: itunesid
    """

    # ajax using POST
    if request.method == 'POST':
        try:
            itunesid = request.POST['itunesid']
            podcast = Podcast.objects.get(itunesid=itunesid)
        except:
            raise Http404()

        eps = podcast.get_episodes()
        episodes_count = len(eps)
        if episodes_count != 1:
            episodes_header = str(episodes_count) + ' episodes of ' + podcast.title
        else:
            episodes_header = str(episodes_count) + ' episode of ' + podcast.title

        context = {
            'episodes_header': episodes_header,
            'episodes': eps,
            'podcast': podcast,
        }
        return render(request, 'episodes.html', context)

def play(request):
    """
    returns html5 audio element
    POST request in a popup
    POST ajax request, in multibar (#player)
    """

    # TODO: itemize episode, get url after redirections
    if request.method == 'POST':
        try:
            url = request.POST['url']
            kind = request.POST['type']
            title = request.POST['title']
            date = request.POST['date']
            itunesid = request.POST['itunesid']
            podcast = Podcast.objects.get(itunesid=itunesid)

            context = {
                'url': url,
                'type': kind,
                'title': title,
                'date': date,
                'podcast': podcast,
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
            except KeyError:
                if request.is_ajax():
                    return render(request, 'login_signup.html', {})
                return redirect('/?next=/podheader/' + itunesid + '/')

            # check whether podcast exists
            try:
                podcast = Podcast.objects.get(itunesid=int(itunesid))
            except Podcast.DoesNotExist:
                if request.is_ajax():
                    return render(request, 'login_signup.html', {})
                return redirect('/?next=/podinfo/' + itunesid + '/')

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
                return render(request, 'login_signup.html', {})
            return redirect('/?next=/podinfo/' + itunesid + '/')
