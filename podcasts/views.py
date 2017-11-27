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
        context = {}
        user = request.user
        podcast = get_object_or_404(Podcast, itunesid=itunesid)

        # mark podcast as subscribed
        podcast.is_subscribed(user)
        context['podcast'] = podcast

        if not request.is_ajax():
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
        itunesid = request.POST.get('itunesid', None)
        try:
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
        episode['url'] = request.POST.get('url')
        episode['type'] = request.POST.get('type')
        episode['title'] = request.POST.get('title')
        episode['podcast'] = request.POST.get('podcast')
        episode['artwork'] = request.POST.get('artwork')
        episode['date'] = request.POST.get('date')
        return render(request, 'player.html', {'episode': episode})

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
        if request.user.is_authenticated:
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
                subscription.delete()
                podcast.n_subscribers -= 1
                podcast.save()

                if request.is_ajax():
                    # this goes on button
                    return HttpResponse('Subscribe')
                return redirect('/podinfo/' + itunesid + '/')

            # if subscription doesn't exist, create it
            except Subscription.DoesNotExist:
                Subscription.objects.create(
                                itunesid=podcast.itunesid,
                                feedUrl=podcast.feedUrl,
                                title=podcast.title,
                                artist=podcast.artist,
                                genre=podcast.genre,
                                n_subscribers=podcast.n_subscribers,
                                explicit=podcast.explicit,
                                language=podcast.language,
                                copyrighttext=podcast.copyrighttext,
                                description=podcast.description,
                                reviewsUrl=podcast.reviewsUrl,
                                artworkUrl=podcast.artworkUrl,
                                podcastUrl=podcast.podcastUrl,
                                user=request.user,
                                pod=podcast,
                )
                podcast.n_subscribers += 1
                podcast.save()

                if request.is_ajax():
                    # this goes on button
                    return HttpResponse('Unsubscribe')
                return redirect('/podinfo/' + itunesid + '/')

        else:
            if request.is_ajax():
                raise Http404()
            return redirect('/account/login/?next=/podinfo/' + itunesid + '/')
