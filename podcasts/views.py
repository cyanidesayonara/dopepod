from django.shortcuts import render, redirect
from django.http import Http404
from .models import Podcast, Subscription, Episode
import logging
from datetime import datetime, timedelta
from django.core import signing

logger = logging.getLogger(__name__)

def episodes(request):
    """
    returns html for episodes
    GET ajax request sent by showpod
    required argument: podid
    """

    # ajax using POST
    if request.method == 'GET':
        podid = request.GET.get('podid', '0')
        try:
            podcast = Podcast.objects.get(podid=int(podid))
        except (ValueError, Podcast.DoesNotExist):
            raise Http404()

        context = {
            'podcast': podcast,
        }

        context = Episode.get_episodes(context, podcast, ajax=True)

        return render(request, 'episodes.html', context)

def play(request):
    """
    returns html5 audio element
    POST request in a popup
    POST ajax request
    """

    # TODO: itemize episode, get url after redirections
    if request.method == 'POST':
        try:
            signature = request.POST['signature']
            data = signing.loads(signature)
            url = data['url']
            kind = data['type']
            title = data['title']
            date = datetime.strptime(data['pubDate'],"%b %d %Y %X %z")
            podid = data['podid']
            description = data['description']
        except (KeyError, signing.BadSignature):
            raise Http404()

        try:
            length = data['length']
            t = datetime.strptime(length,"%H:%M:%S")
            length = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        except (KeyError, ValueError):
            length = None

        try:
            size = data['size']
        except KeyError:
            size = None

        try:
            podcast = Podcast.objects.get(podid=podid)
        except Podcast.DoesNotExist:
            raise Http404()

        episode = Episode.objects.create(
            url=url,
            kind=kind,
            title=title,
            pubDate=date,
            podcast=podcast,
            length=length,
            size=size,
            description=description,
            signature=signature,
        )

        episode.play()

        player = {
            'episode': episode,
        }

        context = {
            'player': player,
        }

        return render(request, 'player.html', context)

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
                podid = request.POST['podid']
                podcast = Podcast.objects.get(podid=int(podid))
            except (ValueError, KeyError, Podcast.DoesNotExist) as e:
                raise Http404()

            podcast.subscribe(user)
            podcast.set_subscribed(user)

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
