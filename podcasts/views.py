from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from .models import Genre, Language, Podcast, Subscription
import string

def charts(request):
    """
    returns podcast charts
    """
    pass
    # try:
    #     genre = request.GET['genre']
    # except:
    #     genre = 'All'
    #
    # try:
    #     genre = request.GET['genre']
    # except:
    #     genre = 'All'
    #
    # try:
    #     explicit = False if request.GET['explicit'] == 'false' else True
    # except:
    #     explicit = True

    # r = requests.get('https://itunes.apple.com/us/rss/toppodcasts/limit=100/genre=1316/xml')
    # data_dict = {}
    # items = []
    # root = ET.fromstring(r.text)
    #
    #     tree = root.find('channel')
    #     data_dict['title'] = tree.find('title').text
    #     data_dict['description'] = tree.find('description').text
    #
    #     ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
    #
    #     for item in tree.findall('item'):
    #         title = item.find('title').text
    #         summary = item.find('description').text
    #         enclosure = item.find('enclosure')
    #         url = enclosure.get('url')
    #         kind = enclosure.get('type')
    #         items.append({'title': title, 'summary': summary, 'url': url, 'kind': kind})
    #     return render(request, 'podinfo.html', {'data': data_dict, 'items': items})

def podinfo(request, itunesid=None):
    """
    returns a podinfo page
    ajax: tracks loaded separately via ajax
    non-ajax: tracks included
    required argument: itunesid
    """

    if request.method == 'GET':
        user = request.user
        podcast = get_object_or_404(Podcast, itunesid=itunesid)

        # mark podcast as subscribed
        podcast.is_subscribed(user)

        if request.is_ajax():
            tracks = {}
        else:
            tracks = podcast.get_tracks()
        return render(request, 'podinfo.html', {'podcast': podcast, 'tracks': tracks})

def tracks(request):
    """
    returns html for tracks
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

        tracks = podcast.get_tracks()
        return render(request, 'tracks.html', {'tracks': tracks})

def play(request, url=None):
    """
    returns html5 audio element
    POST ajax request
    GET request in a popup
    required argument: url
    """

    # GET request, opens in popup
    if request.method == 'GET':
        track = {}
        track['url'] = url
        return render(request, 'player.html', {'track': track})

    # ajax using POST
    # TODO: itemize track
    if request.method == 'POST':
        track = {}
        try:
            track['url'] = request.POST['url']
            track['type'] = request.POST['type']
            # track['title'] = request.POST['title']
        except:
            raise Http404()
        return render(request, 'player.html', {'track': track})

    # any other method not accepted
    else:
        raise Http404()

@login_required
def subscribe(request):
    """
    subscribe to podcast
    """

    # validate request
    if request.method == 'POST':
        try:
            itunesid = request.POST['itunesid']
        except KeyError:
            raise Http404()

        # check whether podcast exists
        try:
            podcast = Podcast.objects.get(itunesid=itunesid)
        except Podcast.DoesNotExist:
            raise Http404()

        # if subscription exists, delete it
        try:
            subscription = Subscription.objects.get(itunesid=itunesid, user=request.user)
            podcast.n_subscribers -= 1
            podcast.save()
            subscription.delete()
            # this goes on button
            return HttpResponse('Subscribe')

        # if subscription doesn't exist, create it
        except Subscription.DoesNotExist:
            podcast.n_subscribers += 1
            podcast.save()
            Subscription.objects.create(
                            itunesid=podcast.itunesid,
                            user=request.user,
                            pod=podcast,
            )
        # this goes on button
        return HttpResponse('Unsubscribe')
    else:
        raise Http404()
