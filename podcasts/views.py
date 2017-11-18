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

def search(request):
    """
    set search terms
    """
    if request.method == 'GET':
        # get query, if any
        try:
            q = request.GET['q']
        except:
            q = None

        if len(q) >= 2:
            context = {}
            # get genre or 'All'
            try:
                genre = request.GET['genre']
            except:
                genre = 'All'

            # get language or 'All'
            try:
                language = request.GET['language']
            except:
                language = 'All'

            # get explicit or True
            try:
                explicit = False if request.GET['explicit'] == 'false' else True
            except:
                explicit = True

            # get user
            user = request.user

            # return podcasts matching search terms
            context['podcasts'] = actual_search(q, genre, language, explicit, user)
        # if query None, return nothing

        if not request.is_ajax():
            context['genres'] = Genre.get_primary_genres(Genre)
            context['languages'] = Language.objects.all()
            context['abc'] = string.ascii_uppercase
        return render(request, 'results.html', context)

def actual_search(q, genre, language, explicit, user):
    """
    return matching podcasts, set subscribed to True on subscribed ones
    """

    # get all podcasts
    podcasts = Podcast.objects.all()

    # filter by explicit
    if explicit == False:
        podcasts = podcasts.filter(explicit=explicit)

    # filter by genre
    if genre != 'All':
        podcasts = podcasts.filter(genre__name=genre)

    # filter by language
    if language != 'All':
        podcasts = podcasts.filter(language__name=language)

    # last but not least, filter by title
    # always return n_results
    n_results = 12
    res = podcasts.filter(title__istartswith=q)[:n_results]


    if len(res) < n_results:
        res2 = podcasts.filter(title__icontains=q)[:(n_results - len(res))]
        # print(res2)
        # for x in res2:
        #     print(x.n_subscribers)
        res = res.union(res2)

        if len(res) < n_results:
            res3 = podcasts.all().order_by('n_subscribers')[:(n_results - len(res))]
            # for x in res3:
            #     print(x.n_subscribers)
            # print(res)
            # print(res3)
            res = res3.union(res)
            res = res.order_by('title')

    # get a list of itunesids from user's subscriptions (if not AnonymousUser)
    if user.username:
        subscriptions = Subscription.objects.filter(user=user).values_list('itunesid', flat=True)
    else:
        subscriptions = []

    for podcast in res:
        if podcast.itunesid in subscriptions:
            podcast.subscribed = True
    return res

def podinfo(request, itunesid=None):
    """
    returns a podinfo page
    ajax: tracks loaded separately via ajax
    non-ajax: tracks included
    required argument: itunesid
    """

    user = request.user

    if request.method == 'GET':
        podcast = get_object_or_404(Podcast, itunesid=itunesid)

        # mark podcast as subscribed
        podcast.is_subscribed(user)

        if request.is_ajax():
            return render(request, 'podinfo.html', {'podcast': podcast})
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
