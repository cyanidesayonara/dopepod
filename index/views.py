from django.shortcuts import render, redirect, Http404, HttpResponse
from django.contrib.auth.models import User
from .forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast, Episode
from django.views.decorators.vary import vary_on_headers
from django.db.models import F
from django.utils import timezone
from datetime import datetime
from allauth.account import views as allauth
import json
import logging

logger = logging.getLogger(__name__)

def get_last_seen(session):
    try:
        last_seen = datetime.strptime(session["last_seen"], "%b %d %Y %X %z")
        cookie = False
    except (KeyError, ValueError):
        last_seen = timezone.now()
        cookie = True
    session["last_seen"] = datetime.strftime(timezone.now(), "%b %d %Y %X %z")
    return (last_seen, cookie) 

def dopebar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == "GET":
        if request.is_ajax():
            return render(request, "dopebar.min.html", {})

@vary_on_headers("Accept")
def index(request):
    """
    returns index page
    with chart & search bar for non-ajax
    """

    if request.method == "GET":
        user = request.user
        view = request.GET.get("view" , None)

        if user.is_authenticated:
            results = {
                "view": "dashboard",
            }
        else:
            results = {
                "view": "splash",
            }

        languages = Language.get_languages()
        genres = Genre.get_primary_genres()

        results.update({
            "languages": languages,
            "genres": genres,
        })

        context = {
            "results": results,
            "view": view,
        }

        if request.is_ajax():
            return render(request, "results_base.min.html", context)

        last_seen, cookie = get_last_seen(request.session)
        last_played = Episode.get_last_played()
        url = request.get_full_path()
        charts = Podcast.search(url=url, provider="dopepod")

        results["extend"] = True

        context.update({
            "cookie_banner": cookie,
            "charts": charts,
            "last_played": last_played,
        })
        return render(request, "results_base.min.html", context)

@vary_on_headers("Accept")
def charts(request):
    """
    returns chart (optional: for requested genre)
    with search bar for non-ajax
    """

    if request.method == "GET":
        user = request.user
        genre = request.GET.get("genre", None)
        try:
            genre = Genre.objects.get(name=genre)
        except Genre.DoesNotExist:
            genre = None
        language = request.GET.get("language", None)
        try:
            language = Language.objects.get(name=language)
        except Language.DoesNotExist:
            language = None

        provider = request.GET.get("provider", None)
        providers = ["dopepod", "itunes"]
        if provider not in providers:
            provider = providers[0]

        url = request.get_full_path()
        results = Podcast.search(
            url=url, provider=provider, genre=genre, language=language
        )

        context = {
            "results": results,
        }

        if request.is_ajax():
            return render(request, "results_base.min.html", context)

        last_seen, cookie = get_last_seen(request.session)
        last_played = Episode.get_last_played()

        context = {
            "cookie_banner": cookie,
            "charts": results,
            "last_played": last_played,
        }

        if user.is_authenticated:
            results = {
                "view": "dashboard",
            }
        else:
            results = {
                "view": "splash",
            }

        languages = Language.get_languages()
        genres = Genre.get_primary_genres()

        results.update({
            "languages": languages,
            "genres": genres,
        })

        results["extend"] = True

        context.update({
            "results": results,
        })

        return render(request, "results_base.min.html", context)

@vary_on_headers("Accept")
def search(request):
    """
    sets search terms
    calls search
    returns results
    with chart & search bar for non-ajax
    """

    if request.method == "GET":
        
        # get q
        q = request.GET.get("q", None)
        if q:
            q = q.strip().lower()
            if len(q) > 30:
                q = q[:30]

        # get genre
        genre = request.GET.get("genre", None)
        if genre:
            try:
                genre = Genre.objects.get(name=genre)
            except Genre.DoesNotExist:
                genre = None

        # get lang
        language = request.GET.get("language", None)
        if language:
            try:
                language = Language.objects.get(name=language)
            except Language.DoesNotExist:
                language = None

        # get view
        view = request.GET.get("view", None)
     
        # page
        page = request.GET.get("page", None)
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        # get show
        show = None

        # get url
        url = request.get_full_path()

        results = Podcast.search(
            url=url, q=q, genre=genre, language=language, show=show, page=page, view=view
        )

        context = {
            "results": results,
        }

        if request.is_ajax():
            return render(request, "results_base.min.html", context)

        charts = Podcast.search(url=url, provider="dopepod")
        last_seen, cookie = get_last_seen(request.session)
        last_played = Episode.get_last_played()

        results["extend"] = True

        context.update({
            "cookie_banner": cookie,
            "charts": charts,
            "last_played": last_played,
        })
        return render(request, "results_base.min.html", context)

@vary_on_headers("Accept")
def subscriptions(request):
    """
    returns subscriptions for user
    with chart & search bar for non-ajax
    """

    if request.method == "GET":
        user = request.user
        if user.is_authenticated:
            results = Subscription.get_subscriptions(user)

            context = {
                "results": results,
            }

            if request.is_ajax():
                return render(request, "results_base.min.html", context)

            url = request.get_full_path()
            charts = Podcast.search(url=url, provider="dopepod")
            last_seen, cookie = get_last_seen(request.session)
            last_played = Episode.get_last_played()

            results["extend"] = True

            context.update({
                "cookie_banner": cookie,
                "charts": charts,
                "last_played": last_played,
            })

            return render(request, "results_base.min.html", context)
        else:
            if request.is_ajax():
                results = {
                    "view": "splash",
                }

                languages = Language.get_languages()
                genres = Genre.get_primary_genres()

                results.update({
                    "languages": languages,
                    "genres": genres,
                })

                return render(request, "results_base.min.html", context)
            return redirect("/")

    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            try:
                podids = request.POST.getlist("podids[]")
                if podids:
                    for podid in podids:
                        podcast = Podcast.objects.get(podid=int(podid))
                        podcast.subscribe_or_unsubscribe(user)
                    results = Subscription.get_subscriptions(user)
                else:
                    podid = request.POST.get("podids")
                    podcast = Podcast.objects.get(podid=int(podid))
                    podcast.subscribe_or_unsubscribe(user)
                    podcast.is_subscribed(user)
                    results = {
                        "view": "showpod",
                        "extra_options": True,
                        "header": podcast.title,
                        "podcast": podcast,
                    }

            except (ValueError, KeyError, TypeError, Podcast.DoesNotExist):
                raise Http404()
            
            context = {
                "results": results,
            }
            
            if request.is_ajax():
                return render(request, "results_base.min.html", context)
            if results.view == "showpod":
                return redirect(podcast.get_absolute_url())
            return redirect("/subscriptions/")
        else:
            if request.is_ajax():
                results = {
                    "view": "splash",
                }

                languages = Language.get_languages()
                genres = Genre.get_primary_genres()

                results.update({
                    "languages": languages,
                    "genres": genres,
                })

                return render(request, "results_base.min.html", context)
            return redirect("/")

@vary_on_headers("Accept")
def playlist(request):
    if request.method == "GET":
        user = request.user
        if user.is_authenticated:
            results = Episode.get_playlist(user)

            context = {
                "results": results,
            }

            if request.is_ajax():
                return render(request, "results_base.min.html", context)

            url = request.get_full_path()
            charts = Podcast.search(url=url, provider="dopepod")
            last_seen, cookie = get_last_seen(request.session)
            last_played = Episode.get_last_played()

            results["extend"] = True

            context.update({
                "cookie_banner": cookie,
                "charts": charts,
                "last_played": last_played,
            })
            return render(request, "results_base.min.html", context)
        else:
            if request.is_ajax():
                results = {
                    "view": "splash",
                }

                languages = Language.get_languages()
                genres = Genre.get_primary_genres()

                results.update({
                    "languages": languages,
                    "genres": genres,
                })

                return render(request, "results_base.min.html", context)
            return redirect("/")

    if request.method == "POST":
        user = request.user
        try:
            mode = request.POST["mode"]
            if mode == "play":
                # returns html5 audio element
                # POST request in a popup
                # POST ajax request

                try:
                    signature = request.POST["signature"]
                    episode = Episode.add(signature, user)
                except KeyError:
                    try:
                        position = int(request.POST["pos"])
                        episode = Episode.objects.get(user=user, position=position)
                    except (KeyError, Episode.DoesNotExist):
                        raise Http404()
                
                episode.play()

                context = {
                    "episode": episode,
                }

                if request.is_ajax():
                    return render(request, "player.min.html", context)
                return render(request, "player.min.html", context)
            if user.is_authenticated:
                if mode == "add":
                    signature = request.POST["signature"]
                    Episode.add(signature, user)
                elif mode == "remove":
                    pos = int(request.POST["pos"])
                    Episode.remove(pos, user)
                elif mode == "up":
                    pos = int(request.POST["pos"])
                    Episode.up(pos, user)
                elif mode == "down":
                    pos = int(request.POST["pos"])
                    Episode.down(pos, user)
                else:
                    raise Http404()
            else:
                raise Http404()
        except (KeyError, TypeError):
            raise Http404()

        results = Episode.get_playlist(user)

        context = {
            "results": results,
        }

        if request.is_ajax():
            return render(request, "results_base.min.html", context)

        url = request.get_full_path()
        charts = Podcast.search(url=url, provider="dopepod")
        last_seen, cookie = get_last_seen(request.session)
        last_played = Episode.get_last_played()

        results["extend"] = True

        context.update({
            "cookie_banner": cookie,
            "charts": charts,
            "last_played": last_played,
        })
        return render(request, "results_base.min.html", context)

@vary_on_headers("Accept")
def showpod(request, podid):
    """
    returns a showpod page
    ajax: episodes loaded separately via ajax
    non-ajax: episodes included + chart & search bar
    required argument: podid
    """

    if request.method == "GET":
        user = request.user
        try:
            podcast = Podcast.objects.get(podid=podid)
            podcast.views = F("views") + 1
            podcast.save()
            podcast.is_subscribed(user)
        except Podcast.DoesNotExist:
            raise Http404

        results = {
            "view": "showpod",
            "extra_options": True,
            "header": podcast.title,
            "podcast": podcast,
        }

        context = {
            "results": results,
        }
        if request.is_ajax():
            return render(request, "results_base.min.html", context)

        # page
        page = request.GET.get("page", None)
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        url = request.get_full_path()
        episodes = Episode.get_episodes(url, podcast.podid, podcast.feedUrl, page)
        for page in episodes:
            results.update(page)
        Episode.set_new(user, podcast.podid, results["episodes"])

        charts = Podcast.search(url=url, provider="dopepod")
        last_seen, cookie = get_last_seen(request.session)
        last_played = Episode.get_last_played()

        results["extend"] = True

        context.update({
            "cookie_banner": cookie,
            "charts": charts,
            "last_played": last_played,
        })
        return render(request, "results_base.min.html", context)

@vary_on_headers("Accept")
def settings(request):
    """
    GET returns settings form
    POST saves settings form, redirects to index
    with chart & search bar for non-ajax
    """

    user = request.user
    if user.is_authenticated:
        results = {
            "header": "Settings",
            "view": "settings",
            "extra_options": True,
        }
        if request.method == "GET":
            context = {
                "results": results,
                "user_form": UserForm(instance=request.user),
                "profile_form": ProfileForm(instance=request.user.profile),
            }

            if request.is_ajax():
                return render(request, "results_base.min.html", context)
            
            url = request.get_full_path()
            charts = Podcast.search(url=url, provider="dopepod")
            last_seen, cookie = get_last_seen(request.session)
            last_played = Episode.get_last_played()

            results["extend"] = True

            context.update({
                "cookie_banner": cookie,
                "charts": charts,
                "last_played": last_played,
            })

            return render(request, "results_base.min.html", context)

        if request.method == "POST":
            user_form = UserForm(instance=request.user, data=request.POST)
            profile_form = ProfileForm(instance=request.user.profile, data=request.POST)

            context = {
                "results": results,
                "user_form": user_form,
                "profile_form": profile_form,
            }

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()

                context.update({
                    "message": "Saved!",
                })

                if request.is_ajax():
                    return render(request, "results_base.min.html", context)
                url = request.get_full_path()
                charts = Podcast.search(url=url, provider="dopepod")
                last_seen, cookie = get_last_seen(request.session)
                last_played = Episode.get_last_played()

                results["extend"] = True

                context.update({
                    "cookie_banner": cookie,
                    "charts": charts,
                    "last_played": last_played,
                })
                return render(request, "results_base.min.html", context)
            else:
                errors = {}

                data = json.loads(user_form.errors.as_json())
                keys = data.keys()
                for key in keys:
                    message = data[key][0]["message"]
                    if message:
                        errors[key] = message

                data = json.loads(profile_form.errors.as_json())
                keys = data.keys()
                for key in keys:
                    message = data[key][0]["message"]
                    if message:
                        errors[key] = message

                context.update({
                    "errors": errors,
                })

                if request.is_ajax:
                    return render(request, "results_base.min.html", context, status=400)

                url = request.get_full_path()
                charts = Podcast.search(url=url, provider="dopepod")
                last_seen, cookie = get_last_seen(request.session)
                last_played = Episode.get_last_played()

                results["extend"] = True

                context.update({
                    "cookie_banner": cookie,
                    "charts": charts,
                    "last_played": last_played,
                })
                return render(request, "results_base.min.html", context)
    else:
        if request.is_ajax():
            return render(request, "splash.min.html", context)
        return redirect("/?next=/settings/")

# allauth stuff
# https://stackoverflow.com/questions/26889178/how-to-redirect-all-the-views-in-django-allauth-to-homepage-index-instead-of-ac

def get_form_errors(data):
    errors = {}
    # non-field errors
    for error in data["form"]["errors"]:
        errors["general"] = error
    # field-specific errors
    for field in data["form"]["fields"]:
        for error in data["form"]["fields"][field]["errors"]:
            if field == "login":
                field = "email"
            errors[field] = error
    try:
        email = data["form"]["fields"]["login"]["value"]
    except KeyError:
        try:
            email = data["form"]["fields"]["email"]["value"]
        except KeyError:
            email = ""
    return (email, errors)

def login(request):
    """
    relays stuff to and from allauth
    kind of dumb but it works
    """

    if request.method == "POST":
        # request sent to allauth is always ajax so the output is json
        ajax = request.is_ajax()
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = allauth.login(request)
        # parse json response
        data = json.loads(response.content)

        results = {}

        context = {
            "results": results,
            "view": "login",
        }

        languages = Language.get_languages()
        genres = Genre.get_primary_genres()

        results.update({
            "languages": languages,
            "genres": genres,
        })

        if response.status_code == 200:
            if ajax:
                results.update({
                    "view": "dashboard",
                })
                return render(request, "results_base.min.html", context)
            return redirect("/")
        else:
            results["view"] = "splash"
            email, errors = get_form_errors(data)
            context.update({
                "errors": errors,
                "email": email,
            })
            if ajax:
                return render(request, "results_base.min.html", context, status=400)
            url = request.get_full_path()
            charts = Podcast.search(url=url, provider="dopepod")
            last_seen, cookie = get_last_seen(request.session)
            last_played = Episode.get_last_played()
            context.update({
                "cookie_banner": cookie,
                "charts": charts,
                "last_played": last_played,
            })
            return render(request, "results_base.min.html", context)
    else:
        return redirect("/?view=login")

def signup(request):
    if request.method == "POST":
        ajax = request.is_ajax()
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = allauth.signup(request)
        data = json.loads(response.content)

        results = {}

        context = {
            "results": results,
            "view": "signup",
        }

        languages = Language.get_languages()
        genres = Genre.get_primary_genres()

        results.update({
            "languages": languages,
            "genres": genres,
        })

        if response.status_code == 200:
            if ajax:
                results.update({
                    "view": "dashboard",
                })
                return render(request, "results_base.min.html", context)
            else:
                return redirect("/")
        else:
            results["view"] = "splash"
            email, errors = get_form_errors(data)
            context.update({
                "errors": errors,
                "email": email,
            })
            if ajax:
                return render(request, "results_base.min.html", context, status=400)
            else:
                url = request.get_full_path()
                charts = Podcast.search(url=url, provider="dopepod")
                last_seen, cookie = get_last_seen(request.session)
                last_played = Episode.get_last_played()
                context.update({
                    "cookie_banner": cookie,
                    "charts": charts,
                    "last_played": last_played,
                })
                return render(request, "results_base.min.html", context)
    else:
        return redirect("/?view=signup")

def logout(request):
    if request.method == "POST":
        response = allauth.logout(request)
        return response

def change_password(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            results = {
                "header": "Settings",
                "view": "settings",
                "extra_options": True,
            }

            context = {
                "results": results,
                "user_form": UserForm(instance=request.user),
                "profile_form": ProfileForm(instance=request.user.profile),
            }

            ajax = request.is_ajax()
            request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
            response = allauth.password_change(request)
            if response.status_code == 200:
                if request.is_ajax():
                    return render(request, "results_base.min.html", context)
                url = request.get_full_path()
                charts = Podcast.search(url=url, provider="dopepod")
                last_seen, cookie = get_last_seen(request.session)
                last_played = Episode.get_last_played()

                results["extend"] = True

                context.update({
                    "cookie_banner": cookie,
                    "charts": charts,
                    "last_played": last_played,
                })
                return render(request, "results_base.min.html", context)
            else:
                languages = Language.get_languages()
                genres = Genre.get_primary_genres()

                results.update({
                    "languages": languages,
                    "genres": genres,
                })
                data = json.loads(response.content)
                email, errors = get_form_errors(data)
                context.update({
                    "errors": errors,
                })
                if ajax:
                    return render(request, "results_base.min.html", context, status=400)
                else:
                    url = request.get_full_path()
                    charts = Podcast.search(url=url, provider="dopepod")
                    last_seen, cookie = get_last_seen(request.session)
                    last_played = Episode.get_last_played()
                    context.update({
                        "cookie_banner": cookie,
                        "charts": charts,
                        "last_played": last_played,
                    })
                    return render(request, "results_base.min.html", context)

def password_reset(request):
    if request.method == "POST":
        ajax = request.is_ajax()
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = allauth.password_reset(request)
        data = json.loads(response.content)

        results = {
            "view": "splash",
        }

        languages = Language.get_languages()
        genres = Genre.get_primary_genres()

        results.update({
            "languages": languages,
            "genres": genres,
        })
        
        if response.status_code == 200:
            context = {
                "results": results,
                "view": "login",
                "message": "We have sent you an e-mail. Please contact us if you do not receive it within a few minutes.",
            }
            
            if ajax:
                return render(request, "results_base.min.html", context)
            else:
                return redirect("/")
        else:
            email, errors = get_form_errors(data)
            context = {
                "results": results,
                "view": "password",
                "errors": errors,
                "email": email,
            }
            if ajax:
                return render(request, "results_base.min.html", context, status=400)
            else:
                url = request.get_full_path()
                charts = Podcast.search(url=url, provider="dopepod")
                last_seen, cookie = get_last_seen(request.session)
                last_played = Episode.get_last_played()

                results["extend"] = True

                context.update({
                    "cookie_banner": cookie,
                    "charts": charts,
                    "last_played": last_played,
                })
                return render(request, "results_base.min.html", context)
    else:
        return redirect("/?view=password")

@vary_on_headers("Accept")
def password_reset_from_key(request, uidb36, key):
    if request.method == "GET":
        ajax = request.is_ajax()
        response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
        if response.status_code == 200:
            request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
            response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
            data = json.loads(response.content)
            email, errors = get_form_errors(data)

            results = {
                "view": "reset_password",
                "extra_options": True,
                "header": "Reset Password",
            }

            context = {
                "errors": errors,
                "results": results,
                "uidb36": uidb36,
                "key": key,
            }

            url = request.get_full_path()
            charts = Podcast.search(url=url, provider="dopepod")
            last_seen, cookie = get_last_seen(request.session)
            last_played = Episode.get_last_played()

            results["extend"] = True

            context.update({
                "cookie_banner": cookie,
                "charts": charts,
                "last_played": last_played,
            })
            return render(request, "results_base.min.html", context)
        else:
            return response

    if request.method == "POST":
        ajax = request.is_ajax()
        response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
        if response.status_code == 200:
            results = {
                "view": "password_reset",
                "extra_options": True,
                "header": "Password Reset",
            }

            context = {
                "results": results,
            }

            if ajax:
                return render(request, "results_base.min.html", context, status=200)
            url = request.get_full_path()
            charts = Podcast.search(url=url, provider="dopepod")
            last_seen, cookie = get_last_seen(request.session)
            last_played = Episode.get_last_played()

            results["extend"] = True

            context.update({
                "cookie_banner": cookie,
                "charts": charts,
                "last_played": last_played,
            })
            return render(request, "results_base.min.html", context, status=200)
        else:
            request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
            response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
            data = json.loads(response.content)
            email, errors = get_form_errors(data)

            results = {
                "view": "reset_password",
                "extra_options": True,
                "header": "Reset Password",
            }

            context = {
                "errors": errors,
                "results": results,
                "uidb36": uidb36,
                "key": key,
            }

            if ajax:
                return render(request, "results_base.min.html", context, status=400)
            else:
                url = request.get_full_path()
                charts = Podcast.search(url=url, provider="dopepod")
                last_seen, cookie = get_last_seen(request.session)
                last_played = Episode.get_last_played()

                results["extend"] = True

                context.update({
                    "cookie_banner": cookie,
                    "charts": charts,
                    "last_played": last_played,
                })
                return render(request, "results_base.min.html", context, status=400)

@vary_on_headers("Accept")
def confirm_email(request, key):
    response = allauth.confirm_email(request, key=key)
    if response.status_code == 200:
        results = {
            "header": "Email Confirmed",
            "view": "confirm_email",
            "extra_options": True,
        }

        context = {
            "results": results,
        }

        if request.is_ajax():
            return render(request, "results_base.min.html", context)

        last_seen, cookie = get_last_seen(request.session)
        last_played = Episode.get_last_played()
        url = request.get_full_path()
        charts = Podcast.search(url=url, provider="dopepod")

        results["extend"] = True

        context.update({
            "cookie_banner": cookie,
            "charts": charts,
            "last_played": last_played,
        })
        return render(request, "results_base.min.html", context)

def noshow(request):
    podid = request.POST.get("podid", None)
    if podid:
        try:
            podcast = Podcast.objects.get(podid=podid)
            podcast.noshow = True
            podcast.save()
        except Podcast.DoesNotExist:
            pass
    return HttpResponse("")

def solong(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            allauth.logout(request)
            user.delete()
    return redirect("/")
