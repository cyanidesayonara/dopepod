from django.shortcuts import render, redirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '#']

def navbar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == 'GET':
        return render(request, 'navbar.html', {})

def index(request):
    if request.method == 'GET':
        context = {
        'alphabet': ALPHABET,
        'selected_alphabet': 'A',
        'search': True,
        }

        if not request.is_ajax():
            user = request.user
            genres = Genre.get_primary_genres()
            chart = Podcast.get_charts(user)
            context['genres'] = genres
            context['chart'] = chart

        return render(request, 'index/index.html', context)

def charts(request):
    if request.method == 'GET':
        genre = request.GET.get('genre', None)
        user = request.user
        genres = Genre.get_primary_genres()
        chart = Podcast.get_charts(user, genre)
        results_info = 'top podcasts in ' + ('All' if genre == None else genre)

        context = {
            'chart': chart,
            'genres': genres,
            'selected_genre': genre,
            'results_info': results_info,
        }

        if not request.is_ajax():
            context['alphabet'] = ALPHABET
            context['selected_alphabet'] = 'A'
            context['search'] = True

        return render(request, 'index/charts.html', context)

def search(request):
    """
    set search terms
    """

    if request.method == 'GET':

        q = request.GET.get('q', None)

        # if query string, return results
        if q:
            user = request.user

            genre = request.GET.get('genre', 'All')
            language = request.GET.get('language', 'All')
            is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
            explicit = is_true(request.GET.get('explicit', 'true'))
            view = request.GET.get('view', 'detail')
            page = int(request.GET.get('page', '1'))
            languages = Language.objects.all()
            genres = Genre.get_primary_genres()

            # return podcasts matching search terms
            podcasts = Podcast.search(genre, language, explicit, user, q=q)

            results_info = str(podcasts.count()) + ' results for "' + q + '"'

            context = {
                'genres': genres,
                'languages': languages,
                'selected_q': q,
                'selected_genre': genre,
                'selected_language': language,
                'selected_view': view,
                'results_info': results_info,
            }

            if not request.is_ajax():
                context['chart'] = Podcast.get_charts(user)
                context['alphabet'] = ALPHABET
                context['search'] = True

            if view == 'detail':
                paginator = Paginator(podcasts, 24)
            else:
                paginator = Paginator(podcasts, 50)

            try:
                context['podcasts'] = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                context['podcasts'] = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                context['podcasts'] = paginator.page(paginator.num_pages)

            if view == 'detail':
                return render(request, 'index/results_detail.html', context)
            else:
                return render(request, 'index/results_list.html', context)

        else:
            if request.is_ajax():
                return render(request, 'index/results_detail.html', {})
            return redirect('index')

def browse(request):
    """
    set browse terms
    """

    user = request.user

    if request.method == 'GET':
        alphabet = request.GET.get('alphabet', 'A')
        languages = Language.objects.all()
        genre = request.GET.get('genre', 'All')
        language = request.GET.get('language', 'All')
        view = request.GET.get('view', 'list')
        page = int(request.GET.get('page', '1'))
        is_true = lambda value: bool(value) and value.lower() not in ('false', '0')
        explicit = is_true(request.GET.get('explicit', 'true'))
        genres = Genre.get_primary_genres()

        podcasts = Podcast.search(genre, language, explicit, user, alphabet=alphabet)

        results_info = str(podcasts.count()) + ' results for "' + alphabet + '"'

        context = {
            'genres': genres,
            'languages': languages,
            'selected_alphabet': alphabet,
            'selected_genre': genre,
            'selected_language': language,
            'selected_view': view,
            'results_info': results_info,
        }

        if not request.is_ajax():
            context['chart'] = Podcast.get_charts(user)
            context['alphabet'] = ALPHABET
            context['browse'] = True


        if view == 'detail':
            paginator = Paginator(podcasts, 24)
        else:
            paginator = Paginator(podcasts, 50)

        try:
            context['podcasts'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['podcasts'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['podcasts'] = paginator.page(paginator.num_pages)

        if view == 'detail':
            return render(request, 'index/results_detail.html', context)
        else:
            return render(request, 'index/results_list.html', context)

def subscriptions(request):
    """
    returns subscription for user
    GET for non-ajax requests
    GET ajax request first returns base.html,
    then requests subscriptions via POST
    """

    user = request.user
    if user.is_authenticated:
        if request.method == 'GET':
            subscriptions = Subscription.get_subscriptions(user)
            results_info = str(subscriptions.count()) + ' subscriptions'

            context = {
                'results_info': results_info,
                'subscriptions': subscriptions,
            }

            if not request.is_ajax():
                genres = Genre.get_primary_genres()
                chart = Podcast.get_charts(user)
                context['genres'] = genres
                context['chart'] = chart
                context['alphabet'] = ALPHABET
                context['selected_alphabet'] = 'A'
                context['search'] = True
            return render(request, 'index/subscriptions.html', context)
    else:
        raise Http404()

def settings(request):
    """
    GET return settings form
    POST save settings form
    """
    user = request.user
    if user.is_authenticated:
        context = {}
        if not request.is_ajax():
            genres = Genre.get_primary_genres()
            chart = Podcast.get_charts(user)
            context['genres'] = genres
            context['chart'] = chart

        if request.method == 'GET':
            context['user_form'] = UserForm(instance=request.user)
            context['profile_form'] = ProfileForm(instance=request.user.profile)
            return render(request, 'index/settings.html', context)

        if request.method == 'POST':
            context['user_form'] = UserForm(instance=request.user)
            context['profile_form'] = ProfileForm(instance=request.user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                return render(request, 'index/settings.html', context)
            else:
                return render(request, 'index/settings.html', context)
    else:
        raise Http404()
