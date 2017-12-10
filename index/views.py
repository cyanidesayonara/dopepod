from django.shortcuts import render, redirect, Http404, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','#']

def navbar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == 'GET':
        return render(request, 'navbar.html', {})

def index(request):
    """
    returns index page
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        if request.is_ajax():
            return render(request, 'index/index.html', {})

        user = request.user
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts()

        # chart and search bar for non-ajax
        context = {
            'chart_results_info': 'top podcasts on itunes',
            'chart_genres': genres,
            'chart': chart,
            'alphabet': ALPHABET,
            'search': True,
        }

        return render(request, 'index/index.html', context)

def charts(request):
    """
    returns chart (optional: for requested genre)
    with search bar for non-ajax
    """

    if request.method == 'GET':
        genre = request.GET.get('genre', None)
        user = request.user
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts(genre)
        results_info = 'top podcasts ' + ('on itunes' if genre == None else 'in ' + str(genre))

        context = {
            'chart': chart,
            'chart_genres': genres,
            'chart_selected_genre': genre,
            'chart_results_info': results_info,
        }

        if request.is_ajax():
            return render(request, 'index/charts.html', context)

        # search bar for non-ajax
        context.update({
            'alphabet': ALPHABET,
            'search': True,
        })

        return render(request, 'index/index.html', context)

def search(request):
    """
    sets search terms
    calls search
    returns results
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        q = request.GET.get('q', None)
        if q:
            user = request.user
            genre = request.GET.get('genre', None)
            language = request.GET.get('language', None)
            page = int(request.GET.get('page', '1'))
            languages = Language.objects.all()
            genres = Genre.get_primary_genres()

            podcasts = Podcast.search(genre, language, user, q=q)
            paginator = Paginator(podcasts, 24)
            results_info = str(paginator.count) + ' results for "' + q + '"'

            try:
                podcasts = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                podcasts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                podcasts = paginator.page(paginator.num_pages)

            context = {
                'genres': genres,
                'languages': languages,
                'selected_q': q,
                'selected_genre': genre,
                'selected_language': language,
                'results_info': results_info,
                'podcasts': podcasts,
            }

            if request.is_ajax():
                return render(request, 'index/results_detail.html', context)

            context.update({
                'search': True,
                'chart': Podcast.get_charts(),
                'alphabet': ALPHABET,
                'chart_results_info': 'top podcasts on itunes',
            })

            return render(request, 'index/results_detail.html', context)
        return render(request, 'index/results_detail.html', {})

def browse(request):
    """
    sets browse terms
    calls search
    returns results
    with chart & browse bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        genre = request.GET.get('genre', None)
        language = request.GET.get('language', None)
        page = int(request.GET.get('page', '1'))
        languages = Language.objects.all()
        genres = Genre.get_primary_genres()
        alphabet = request.GET.get('alphabet', 'A')

        podcasts = Podcast.search(genre, language, user, alphabet=alphabet)
        paginator = Paginator(podcasts, 120)
        results_info = str(paginator.count) + ' results for "' + alphabet + '"'

        try:
            podcasts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            podcasts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            podcasts = paginator.page(paginator.num_pages)

        context = {
            'genres': genres,
            'languages': languages,
            'selected_alphabet': alphabet,
            'selected_genre': genre,
            'selected_language': language,
            'results_info': results_info,
            'podcasts': podcasts,
            'podcasts1': podcasts[:40],
            'podcasts2': podcasts[40:80],
            'podcasts3': podcasts[80:120],
        }

        if request.is_ajax():
            return render(request, 'index/results_list.html', context)

        # chart & browse bar for non-ajax
        context.update({
            'browse': True,
            'chart': Podcast.get_charts(),
            'alphabet': ALPHABET,
            'chart_results_info': 'top podcasts on itunes',
        })
        return render(request, 'index/results_list.html', context)

def subscriptions(request):
    """
    returns subscriptions for user
    with chart & search bar for non-ajax
    """

    if request.method == 'GET':
        user = request.user
        if user.is_authenticated:
            subs = Subscription.get_subscriptions(user)
            results_info = str(subs.count()) + ' subscriptions'

            context = {
                'results_info': results_info,
                'subscriptions': subs,
            }

            if request.is_ajax():
                return render(request, 'index/subscriptions.html', context)

            # chart & search bar for non-ajax
            genres = Genre.get_primary_genres()
            chart = Podcast.get_charts()
            context.update({
                'search': True,
                'genres': genres,
                'chart': chart,
                'alphabet': ALPHABET,
                'chart_results_info': 'top podcasts on itunes',
            })
            return render(request, 'index/subscriptions.html', context)

        else:
            if request.is_ajax():
                raise Http404()
            return redirect('/account/login/?next=/subscriptions/')

def podinfo(request, itunesid):
    """
    returns a podinfo page
    ajax: episodes loaded separately via ajax
    non-ajax: episodes included + chart & search bar
    required argument: itunesid
    """

    if request.method == 'GET':
        user = request.user
        podcast = get_object_or_404(Podcast, itunesid=itunesid)

        if user.is_authenticated:
            podcast.set_subscribed(user)

        context = {
            'podcast': podcast,
        }

        if request.is_ajax():
            return render(request, 'podinfo.html', context)

        # chart & search bar
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts()
        context.update({
            'chart_genres': genres,
            'chart': chart,
            'alphabet': ALPHABET,
            'search': True,
            'episodes': podcast.get_episodes(),
        })
        return render(request, 'podinfo.html', context)

def settings(request):
    """
    GET returns settings form
    POST saves settings form, redirects to index
    with chart & search bar for non-ajax
    """

    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':

            context = {
                'user_form': UserForm(instance=request.user),
                'profile_form': ProfileForm(instance=request.user.profile),
            }

            if request.is_ajax():
                return render(request, 'index/settings.html', context)

            # chart & search bar
            genres = Genre.get_primary_genres()
            chart = Podcast.get_charts()
            context.update({
                'chart_genres': genres,
                'chart': chart,
                'alphabet': ALPHABET,
                'search': True,
            })
            return render(request, 'index/settings.html', context)

        if request.method == 'POST':
            user_form = UserForm(request.POST)
            profile_form = ProfileForm(request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                if request.is_ajax():
                    return render(request, 'index/settings.html', {})
                return redirect('/')
            else:
                context = {
                    'user_form': user_form,
                    'profile_form': profile_form,
                }

                if request.is_ajax():
                    return render(request, 'index/settings.html', context)

                # chart & search bar
                genres = Genre.get_primary_genres()
                chart = Podcast.get_charts()
                context.update({
                    'chart_genres': genres,
                    'chart': chart,
                    'alphabet': ALPHABET,
                    'search': True,
                })
                return render(request, 'index/settings.html', context)
    else:
        if request.is_ajax():
            raise Http404()
        return redirect('/account/login/?next=/settings/')
