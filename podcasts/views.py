from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from .models import Genre, Language, Podcast, Subscription

def podinfo(request, itunesid):
    """
    returns a podinfo page
    ajax: episodes loaded separately via ajax
    non-ajax: episodes included
    required argument: itunesid
    """

    if request.method == 'GET':
        user = request.user
        podcast = get_object_or_404(Podcast, itunesid=itunesid)

        podcast.set_subscribed(user)
        context = {
            'podcast': podcast,
        }

        if not request.is_ajax():
            context['search'] = True
            context['episodes'] = podcast.get_episodes()
        return render(request, 'podinfo.html', context)

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
        context = {}
        context['episodes'] = podcast.get_episodes()
        return render(request, 'episodes.html', context)

def play(request):
    """
    returns html5 audio element
    POST request in a popup
    POST ajax request, bottom of page (#player)
    """

    # TODO: itemize episode
    if request.method == 'POST':
        episode = {}
        try:
            episode['url'] = request.POST['url']
            episode['type'] = request.POST['type']
            episode['title'] = request.POST['title']
            episode['podcast'] = request.POST['podcast']
            episode['artwork'] = request.POST['artwork']
            episode['date'] = request.POST['date']
            return render(request, 'player.html', {'episode': episode})
        except KeyError:
            raise Http404()

def subscribe(request):
    """
    subscribe to podcast via POST request
    delete existing subscription or create a new one
    ajax update button with appropriate value
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
                raise Http404()

            # check whether podcast exists
            try:
                podcast = Podcast.objects.get(itunesid=itunesid)
            except Podcast.DoesNotExist:
                raise Http404()

            subscribed = podcast.subscribe(user)

            if request.is_ajax():
                # this goes on button
                if subscribed:
                    return HttpResponse('Unsubscribe')
                return HttpResponse('Subscribe')
            return redirect('/podinfo/' + itunesid + '/')

        else:
            if request.is_ajax():
                raise Http404()
            return redirect('/account/login/?next=/podinfo/' + itunesid + '/')
