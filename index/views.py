from django.shortcuts import render, redirect, Http404, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from index.forms import ProfileForm, UserForm
from podcasts.models import Genre, Language, Subscription, Podcast, Episode
from django.views.decorators.vary import vary_on_headers
from django.db.models import F
from django.utils import timezone
from datetime import datetime
from allauth.account import views as allauth
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core import serializers
from lazysignup.decorators import allow_lazy_user
from lazysignup.utils import is_lazy_user
from lazysignup import views as lazysignup
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

def get_carousel():
    languages = []
    genres = []
    for language in Language.get_languages():
        languages.append(Podcast.search(url="/", provider="dopepod", language=language, show=6,))
    for genre in Genre.get_primary_genres():
        genres.append(Podcast.search(url="/", provider="dopepod", genre=genre, show=6,))
    results = {
        "view": "carousel",
        "languages": languages,
        "genres": genres,
    }
    return results

def get_donuts(results, user):
    subscriptions_count = Subscription.objects.filter(user=user).count()
    playlist_count = Episode.objects.filter(user=user).count()
    results.update({
        "subscriptions_count": subscriptions_count,
        "playlist_count": playlist_count,
    })
    return results

def render_splash(request, template, context, response=False):
    results = {
        "view": "splash",
        "listen": "podcast name"
    }
    previous = Episode.get_previous()
    context.update({
        "results": results,
        "previous": previous,
    })
    if response:
        context = get_form_errors(context, response)
        if request.is_ajax():
            return render(request, template, context, status=400)
        return render_non_ajax(request, template, context)
    if request.is_ajax():
        return render(request, template, context)
    return redirect("/")

def render_dashboard(request, template, context):
    results = {
        "view": "dashboard",
    }
    results = get_donuts(results, request.user)
    context.update({
        "results": results,
    })
    return render(request, template, context)

def render_non_ajax(request, template, context):
    last_seen, cookie = get_last_seen(request.session)
    url = request.get_full_path()
    previous = Episode.get_previous()
    charts = Podcast.search(url=url, provider="dopepod")
    carousel = get_carousel()
    context["results"]["extend"] = True
    context.update({
        "cookie_banner": cookie,
        "charts": charts,
        "previous": previous,
        "carousel": carousel,
    })
    return render(request, template, context)

def get_settings_errors(context, user_form, profile_form):
    errors = {}
    data = json.loads(user_form.errors.as_json())
    keys = data.keys()
    for key in keys:
        message = data[key][0]["message"]
        if message:
            errors[key] = message
    data = json.loads(profile_form.errors.as_json())
    print(data)
    keys = data.keys()
    for key in keys:
        message = data[key][0]["message"]
        if message:
            errors[key] = message
    context.update({
        "errors": errors,
    })
    return context

def get_form_errors(context, response):
    errors = {}
    data = json.loads(response.content)
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
    context.update({
        "errors": errors,
        "email": email,
    })
    return context

def get_settings_forms(context, request):
    if request.user.is_authenticated:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        context.update({
            "user_form": user_form,
            "profile_form": profile_form,
        })
    return context

def post_settings_forms(context, request):
    user_form = UserForm(instance=request.user, data=request.POST)
    profile_form = ProfileForm(instance=request.user.profile, data=request.POST)
    context.update({
        "user_form": user_form,
        "profile_form": profile_form,
    })
    if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        context.update({
            "message": "Saved!",
        })
        return context, True
    else:
        context = get_settings_errors(context, user_form, profile_form)
        return context, False

def post_contact_form(context, request):
    title = request.POST.get("title", "No title")
    message = request.POST.get("message", "No message")
    email = request.POST.get("email", "no@email.com")
    try:
        validate_email(email)
        send_mail(title, message, email, ['cyanidesayonara@gmail.com'])
        context.update({
            "message": "Sent!",
        })
        return context, True
    except ValidationError:
        errors = {
            "general": "Invalid email",
        }
        context.update({
            "errors": errors,
        })
        return context, False

def get_search_results(request, api=False):
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

    # get order
    order = request.GET.get("order", None)

    if api:
        view = None
        page = None
        show = request.GET.get("show", None)
        try:
            show = int(show)
            if show > 200:
                show = 200
            elif show < 1:
                raise ValueError()
        except (TypeError, ValueError):
            show = 50
    else:
        # get view
        view = request.GET.get("view", None)

        # page
        page = request.GET.get("page", None)
        try:
            page = int(page)
            if page < 1:
                raise ValueError()
        except (TypeError, ValueError):
            page = 1

        # get show
        show = None

    # get url
    url = request.get_full_path()

    results = Podcast.search(
        url=url, q=q, genre=genre, language=language, show=show, page=page, order=order, view=view, api=api,
    )
    return results

def get_showpod_results(podid, user=None, count=None, api=None):
    try:
        podcast = Podcast.objects.get(podid=podid)
    except Podcast.DoesNotExist:
        raise Http404
    if api:
        podcasts = serializers.serialize(api, [podcast], fields=(
            "podid", "feedUrl", "title", "artist", "genre", "explicit", "language", "ccopyrighttext", "description", "reviewsUrl", "podcastUrl", "artworkUrl"
            )
        )
        if api == "json":
            podcasts = json.loads(podcasts)
            count = len(podcasts)

            results = {
                "count": count,
                "results": [],
            }

            for podcast in podcasts:
                results["results"].append(podcast['fields'])
            results = json.dumps(results)
        elif api == "xml":
            results = podcasts
    else:
        results = {
            "view": "showpod",
            "podcast": podcast,
            "options": True,
            "extra_options": True,
            "header": podcast.title,
        }
        podcast.is_subscribed(user)
        # showpod
        if count:
            podcast.views = F("views") + 1
            podcast.save()
    return results

def get_settings_results():
    results = {
        "header": "Settings",
        "view": "settings",
        "options": True,
        "extra_options": True,
    }
    return results

def get_reset_password_results():
    results = {
        "view": "reset_password",
        "extra_options": True,
        "header": "Reset Password",
    }
    return results

def get_password_reset_results():
    results = {
        "view": "password_reset",
        "extra_options": True,
        "header": "Password Reset",
    }
    return results

def get_confirm_email_results():
    results = {
        "view": "confirm_email",
        "extra_options": True,
        "header": "Email Confirmed",
    }
    return results

def get_privacy_results():
    results = {
        "view": "privacy",
        "extra_options": True,
        "header": "Privacy Policy",
    }
    return results

def get_terms_results():
    results = {
        "view": "terms",
        "extra_options": True,
        "header": "Terms of Service",
    }
    return results

def get_contact_results():
    results = {
        "view": "contact",
        "extra_options": True,
        "header": "Contact",
    }
    return results

def get_api_results():
    results = {
        "view": "api",
        "extra_options": True,
        "header": "API",
        "languages": Language.get_languages(),
        "genres": Genre.get_primary_genres(),
    }
    return results

def dopebar(request):
    """
    returns navbar (for refreshing)
    """

    if request.method == "GET" and request.is_ajax():
        return render(request, "dopebar.min.html", {})

@vary_on_headers("Accept")
def api(request):
    if request.method == "GET":
        if request.path == "/api/json/" or request.path == "/api/xml/":
            api = request.path.split("/")[2]
            podid = request.GET.get("podid", None)
            if podid:
                results = get_showpod_results(podid, api=api)
            else:
                results = get_search_results(request, api=api)
            return HttpResponse(results, content_type="text/" + api)
        else:
            template = "results_base.min.html"
            results = get_api_results()
            context = {
                "results": results,
            }
            if request.is_ajax():
                return render(request, template, context)
            return render_non_ajax(request, template, context)
    return redirect("/api/")

@vary_on_headers("Accept")
def index(request):
    """
    returns index page
    with chart & search bar for non-ajax
    """

    if request.method == "GET":
        template = "results_base.min.html"
        user = request.user
        view = request.GET.get("view" , None)
        context = {
            "view": view,
        }
        if request.is_ajax():
            if user.is_authenticated:
                return render_dashboard(request, template, context)
            else:
                return render_splash(request, template, context)
        results = {}
        if user.is_authenticated:
            results = get_donuts(results, user)
            results["view"] = "dashboard"
        else:
            results["view"] = "splash"
            results["listen"] = "podcast name"
        context.update({
            "results": results,
        })
        return render_non_ajax(request, template, context)

@vary_on_headers("Accept")
def charts(request):
    """
    returns chart (optional: for requested genre)
    with search bar for non-ajax
    """

    if request.method == "GET":
        template = "results_base.min.html"
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
            return render(request, template, context)
        if user.is_authenticated:
            results["view"] = "dashboard"
        else:
            results["view"] = "splash"
        return render_non_ajax(request, template, context)

@vary_on_headers("Accept")
def search(request):
    """
    sets search terms
    calls search
    returns results
    with chart & search bar for non-ajax
    """

    if request.method == "GET":
        template = "results_base.min.html"

        results = get_search_results(request)

        context = {
            "results": results,
        }

        if request.is_ajax():
            return render(request, template, context)
        return render_non_ajax(request, template, context)

@vary_on_headers("Accept")
def subscriptions(request):
    """
    returns subscriptions for user
    with chart & search bar for non-ajax
    """

    if request.method == "GET":
        template = "results_base.min.html"
        user = request.user
        if user.is_authenticated:
            results = Subscription.get_subscriptions(user)
            context = {
                "results": results,
            }
            if request.is_ajax():
                return render(request, template, context)
            return render_non_ajax(request, template, context)
        return redirect("/")

    if request.method == "POST":
        template = "results_base.min.html"
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
                    podid = int(request.POST.get("podids"))
                    results = get_showpod_results(podid, user)
                    results["podcast"].subscribe_or_unsubscribe(user)
            except (ValueError, KeyError, TypeError, Podcast.DoesNotExist):
                raise Http404()
            if request.is_ajax():
                context = {
                    "results": results,
                }
                return render(request, template, context)
            if not podids:
                return redirect(podcast.get_absolute_url())
            return redirect("/subscriptions/")
    return redirect("/")

@vary_on_headers("Accept")
def privacy(request):
    if request.method == "GET":
        template = "results_base.min.html"
        results = get_privacy_results()
        context = {
            "results": results,
        }
        if request.is_ajax():
            return render(request, template, context)
        return render_non_ajax(request, template, context)
    return redirect("/privacy/")

@vary_on_headers("Accept")
def terms(request):
    if request.method == "GET":
        template = "results_base.min.html"
        results = get_terms_results()
        context = {
            "results": results,
        }
        if request.is_ajax():
            return render(request, template, context)
        return render_non_ajax(request, template, context)
    return redirect("/terms/")

@vary_on_headers("Accept")
def contact(request):
    template = "results_base.min.html"
    results = get_contact_results()
    context = {
        "results": results,
    }
    if request.method == "GET":
        if request.is_ajax():
            return render(request, template, context)
        return render_non_ajax(request, template, context)
    if request.method == "POST":
        context, valid = post_contact_form(context, request)
        if valid:
            if request.is_ajax():
                return render(request, template, context)
            return render_non_ajax(request, template, context)
        else:
            if request.is_ajax:
                return render(request, template, context, status=400)
            return render_non_ajax(request, template, context)
    return redirect("/contact/")

@vary_on_headers("Accept")
def playlist(request):
    if request.method == "GET":
        template = "results_base.min.html"
        user = request.user
        if user.is_authenticated:
            results = Episode.get_playlist(user)
            context = {
                "results": results,
            }
            if request.is_ajax():
                return render(request, template, context)
            return render_non_ajax(request, template, context)
        return redirect("/")

    if request.method == "POST":
        user = request.user
        try:
            mode = request.POST["mode"]
            if mode == "play":
                template = "player.min.html"
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
                    return render(request, template, context)
                return render_non_ajax(request, template, context)
            if user.is_authenticated:
                template = "results_base.min.html"
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

                results = Episode.get_playlist(user)
                context = {
                    "results": results,
                }
                if request.is_ajax():
                    return render(request, template, context)
                return render_non_ajax(request, template, context)
        except (KeyError, TypeError):
            raise Http404()
    return redirect("/")

@vary_on_headers("Accept")
def showpod(request, podid):
    """
    returns a showpod page
    ajax: episodes loaded separately via ajax
    non-ajax: episodes included + chart & search bar
    required argument: podid
    """

    if request.method == "GET":
        template = "results_base.min.html"
        user = request.user
        results = get_showpod_results(podid, user, count=True)
        context = {
            "results": results,
        }
        if request.is_ajax():
            return render(request, template, context)

        # page
        page = request.GET.get("page", None)
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1

        podcast = results["podcast"]
        url = request.get_full_path()
        episodes = Episode.get_episodes(url, podcast, page)
        for page in episodes:
            results.update(page)
        Episode.set_new(user, podcast, results["episodes"])
        return render_non_ajax(request, template, context)

@vary_on_headers("Accept")
def settings(request):
    """
    GET returns settings form
    POST saves settings form, redirects to index
    with chart & search bar for non-ajax
    """

    user = request.user
    if user.is_authenticated:
        template = "results_base.min.html"
        results = get_settings_results()
        context = {
            "results": results,
        }
        if request.method == "GET":
            context = get_settings_forms(context, request)
            if request.is_ajax():
                return render(request, template, context)
            return render_non_ajax(request, template, context)
        if request.method == "POST":
            context, valid = post_settings_forms(context, request)
            if valid:
                if request.is_ajax():
                    return render(request, template, context)
                return render_non_ajax(request, template, context)
            else:
                if request.is_ajax:
                    return render(request, template, context, status=400)
                return render_non_ajax(request, template, context)
    return redirect("/")

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
            results = get_showpod_results(podid, user)
            context = {
                "results": results,
            }

            # page
            page = request.GET.get("page", None)
            try:
                page = int(page)
            except (TypeError, ValueError):
                page = 1

            podcast = results["podcast"]
            url = request.get_full_path()
            episodes = Episode.get_episodes(url, podcast, page)
            for page in episodes:
                results.update(page)
            Episode.set_new(user, podcast, results["episodes"])
            return render(request, "episodes.min.html", context)
        return redirect("/showpod/" + podid + "/")

def previous(request):
    """
    returns previously played
    """

    if request.method == "GET":
        if request.is_ajax():
            template = "results_base.min.html"
            results = Episode.get_previous()
            context = {
                "results": results,
            }
            return render(request, template, context)
        else:
            return redirect("/")

# allauth stuff
# https://stackoverflow.com/questions/26889178/how-to-redirect-all-the-views-in-django-allauth-to-homepage-index-instead-of-ac

def login(request):
    """
    relays stuff to and from allauth
    kinda dumb but it works ¯\_(ツ)_/¯
    """

    if request.method == "POST":
        template = "results_base.min.html"
        # request sent to allauth is always ajax so the output is json
        ajax = request.META["HTTP_X_REQUESTED_WITH"]
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = allauth.login(request)
        request.META["HTTP_X_REQUESTED_WITH"] = ajax
        context = {
            "view": "login",
        }
        user = request.user
        if response.status_code == 200:
            if user.is_authenticated:
                return render_dashboard(request, template, context)
            context.update({
                "message": "You must confirm your email before logging in."
            })
        context = get_form_errors(context, response)
        return render_splash(request, template, context, response=response)
    return redirect("/?view=login")

def signup(request):
    if request.method == "POST":
        template = "results_base.min.html"
        try:
            ajax = request.META["HTTP_X_REQUESTED_WITH"]
        except KeyError:
            ajax = None
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = allauth.signup(request)
        request.META["HTTP_X_REQUESTED_WITH"] = ajax
        context = {}
        if response.status_code == 200:
            context.update({
                "view": "login",
                "message": "We have sent a confirmation link to your email address. Please contact us if you do not receive it within a few minutes."
            })
            return render_splash(request, template, context)
        context.update({
            "view": "signup",
        })
        return render_splash(request, template, context, response=response)
    return redirect("/?view=signup")

def logout(request):
    if request.method == "POST":
        user = request.user
        response = allauth.logout(request)
        # lazy users are deleted on logout
        if is_lazy_user(user):
            user.delete()
        return response

def change_password(request):
    if request.method == "POST":
        template = "results_base.min.html"
        user = request.user
        if user.is_authenticated:
            results = get_settings_results()
            context = {
                "results": results,
            }
            context = get_settings_forms(context, request)
            ajax = request.META["HTTP_X_REQUESTED_WITH"]
            request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
            response = allauth.password_change(request)
            request.META["HTTP_X_REQUESTED_WITH"] = ajax
            if response.status_code == 200:
                context.update({
                    "message": "Password Changed!"
                })
                return render(request, template, context)
            context = get_form_errors(context, response)
            return render(request, template, context)
        return render_splash(request, template, context)
    return redirect("/settings/")

def password_reset(request):
    if request.method == "POST":
        template = "results_base.min.html"
        ajax = request.META["HTTP_X_REQUESTED_WITH"]
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = allauth.password_reset(request)
        request.META["HTTP_X_REQUESTED_WITH"] = ajax

        results = {
            "view": "splash",
        }
        context = {
            "results": results,
        }
        
        if response.status_code == 200:
            context.update({
                "view": "login",
                "message": "We have sent you an email. Please contact us if you do not receive it within a few minutes.",
            })
            return render_splash(request, template, context)
        else:
            context = get_settings_forms(context, request)
            context.update({
                "view": "password",
            })
            return render_splash(request, template, context, response=response)
    return redirect("/?view=password")

def password_reset_from_key(request, uidb36, key):
    template = "results_base.min.html"
    if request.method == "GET":
        response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
        if response.status_code == 200:
            request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
            response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
            del request.META["HTTP_X_REQUESTED_WITH"]

            results = get_reset_password_results()
            context = {
                "results": results,
                "uidb36": uidb36,
                "key": key,
            }
            context = get_form_errors(context, response)
            return render_non_ajax(request, template, context)
        else:
            return response

    if request.method == "POST":
        ajax = request.META["HTTP_X_REQUESTED_WITH"]
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = allauth.password_reset_from_key(request, uidb36=uidb36, key=key)
        request.META["HTTP_X_REQUESTED_WITH"] = ajax

        if response.status_code == 200:
            results = get_password_reset_results()
            context = {
                "results": results,
            }
            if request.is_ajax():
                return render(request, template, context)
            return render_non_ajax(request, template, context)
        else:
            results = get_reset_password_results()
            context = {
                "results": results,
                "uidb36": uidb36,
                "key": key,
            }
            context = get_form_errors(context, response)
            if request.is_ajax():
                return render(request, template, context, status=400)
            return render_non_ajax(request, template, context)
    return redirect("/")

def confirm_email(request, key):
    if request.method == "GET":
        template = "results_base.min.html"
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"
        response = allauth.confirm_email(request, key=key)
        del request.META["HTTP_X_REQUESTED_WITH"]
        results = get_confirm_email_results()
        context = {
            "results": results,
        }
        if response.status_code == 302:
            return render_non_ajax(request, template, context)
    return redirect("/")

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

def tz(request):
    tz = request.POST.get('tz', None)
    if tz:
        request.session['django_timezone'] = tz
    return HttpResponse("")

def solong(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            allauth.logout(request)
            user.delete()
    return redirect("/")

@allow_lazy_user
def tryout(request):
    if request.method == "POST":
        template = "results_base.min.html"
        context = {}
        return render_dashboard(request, template, context)
    return redirect("/")
