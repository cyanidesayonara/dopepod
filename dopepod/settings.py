"""
Django settings for dopepod project.

Generated by "django-admin startproject" using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

# pip upgrade line for windows: for /F "delims===" %i in ('pip freeze -l') do pip install -U %i
# for linux: pip install `pip freeze -l | cut --fields=1 -d = -` --upgrade
# pip install elasticsearch==5.5.3

import os
import local_settings

AUTH_USER_MODEL = "auth.User"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 50000

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

# The simplest case: just add the domain name(s) and IP addresses of your Django server
# ALLOWED_HOSTS = [ "example.com", "203.0.113.5"]
# To respond to "example.com" and any subdomains, start the domain with a dot
# ALLOWED_HOSTS = [".example.com", "203.0.113.5"]

ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    "index",
    "podcasts",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "django.contrib.sites",

    "django_extensions",

    "haystack",

    "sendgrid",

    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # ... include the providers you want to enable:
    "allauth.socialaccount.providers.facebook",
    # "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    # "allauth.socialaccount.providers.reddit",

    "lazysignup",
]

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dopepod.middleware.local_date_middleware.LocalDateMiddleware",
]

if DEBUG:
    INSTALLED_APPS = [
        'debug_toolbar',
    ] + INSTALLED_APPS
    INTERNAL_IPS = [
        '127.0.0.1',
    ]
    MIDDLEWARE = MIDDLEWARE + [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
    "lazysignup.backends.LazySignupBackend",
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack_elasticsearch.elasticsearch5.Elasticsearch5SearchEngine",
        "URL": "http://127.0.0.1:9200/",
        "INDEX_NAME": "haystack",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}

# django.contrib.sites
SITE_ID = local_settings.SITE_ID

# django-allauth settings
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_PASSWORD_MIN_LENGTH = 8
SOCIALACCOUNT_EMAIL_REQUIRED = False
# SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_ADAPTER = "dopepod.adapter.MyLoginAccountAdapter"
LOGIN_REDIRECT_URL = "/"
ACCOUNT_USERNAME_BLACKLIST = [
    ".htaccess", ".htpasswd", ".well-known", "400", "401", "403", "404", "405", "406", "407", "408", "409", "410", "411", "412", "413", "414", "415", "416", "417", "421", "422", "423", "424", "426", "428", "429", "431", "500", "501", "502", "503", "504", "505", "506", "507", "508", "509", "510", "511", "about", "about-us", "abuse", "access", "account", "accounts", "ad", "add", "admin", "administration", "administrator", "ads", "advertise", "advertising", "aes128-ctr", "aes128-gcm", "aes192-ctr", "aes256-ctr", "aes256-gcm", "affiliate", "affiliates", "ajax", "alert", "alerts", "alpha", "amp", "analytics", "api", "app", "apps", "asc", "assets", "atom", "auth", "authentication", "authorize", "autoconfig", "autodiscover", "avatar", "backup", "banner", "banners", "beta", "billing", "billings", "blog", "blogs", "board", "bookmark", "bookmarks", "broadcasthost", "business", "buy", "cache", "calendar", "campaign", "captcha", "careers", "cart", "cas", "categories", "category", "cdn", "cgi", "cgi-bin", "chacha20-poly1305", "change", "channel", "channels", "chart", "chat", "checkout", "clear", "client", "close", "cms", "com", "comment", "comments", "community", "compare", "compose", "config", "connect", "contact", "contest", "cookies", "copy", "copyright", "count", "create", "crossdomain.xml", "css", "curve25519-sha256", "customer", "customers", "customize", "dashboard", "db", "deals", "debug", "delete", "desc", "dev", "developer", "developers", "diffie-hellman-group-exchange-sha256", "diffie-hellman-group14-sha1", "disconnect", "discuss", "dns", "dns0", "dns1", "dns2", "dns3", "dns4", "docs", "documentation", "domain", "download", "downloads", "downvote", "draft", "drop", "ecdh-sha2-nistp256", "ecdh-sha2-nistp384", "ecdh-sha2-nistp521", "edit", "editor", "email", "enterprise", "error", "errors", "event", "events", "example", "exception", "exit", "explore", "export", "extensions", "false", "family", "faq", "faqs", "favicon.ico", "features", "feed", "feedback", "feeds", "file", "files", "filter", "follow", "follower", "followers", "following", "fonts", "forgot", "forgot-password", "forgotpassword", "form", "forms", "forum", "forums", "friend", "friends", "ftp", "get", "git", "go", "group", "groups", "guest", "guidelines", "guides", "head", "header", "help", "hide", "hmac-sha", "hmac-sha1", "hmac-sha1-etm", "hmac-sha2-256", "hmac-sha2-256-etm", "hmac-sha2-512", "hmac-sha2-512-etm", "home", "host", "hosting", "hostmaster", "htpasswd", "http", "httpd", "https", "humans.txt", "icons", "images", "imap", "img", "import", "info", "insert", "investors", "invitations", "invite", "invites", "invoice", "is", "isatap", "issues", "it", "jobs", "join", "js", "json", "keybase.txt", "learn", "legal", "license", "licensing", "limit", "live", "load", "local", "localdomain", "localhost", "lock", "login", "logout", "lost-password", "mail", "mail0", "mail1", "mail2", "mail3", "mail4", "mail5", "mail6", "mail7", "mail8", "mail9", "mailer-daemon", "mailerdaemon", "map", "marketing", "marketplace", "master", "me", "media", "member", "members", "message", "messages", "metrics", "mis", "mobile", "moderator", "modify", "more", "mx", "my", "net", "network", "new", "news", "newsletter", "newsletters", "next", "nil", "no-reply", "nobody", "noc", "none", "noreply", "notification", "notifications", "ns", "ns0", "ns1", "ns2", "ns3", "ns4", "ns5", "ns6", "ns7", "ns8", "ns9", "null", "oauth", "oauth2", "offer", "offers", "online", "openid", "order", "orders", "overview", "owner", "page", "pages", "partners", "passwd", "password", "pay", "payment", "payments", "photo", "photos", "pixel", "plans", "plugins", "policies", "policy", "pop", "pop3", "popular", "portfolio", "post", "postfix", "postmaster", "poweruser", "preferences", "premium", "press", "previous", "pricing", "print", "privacy", "privacy-policy", "private", "prod", "product", "production", "profile", "profiles", "project", "projects", "public", "purchase", "put", "quota", "redirect", "reduce", "refund", "refunds", "register", "registration", "remove", "replies", "reply", "report", "request", "request-password", "reset", "reset-password", "response", "return", "returns", "review", "reviews", "robots.txt", "root", "rootuser", "rsa-sha2-2", "rsa-sha2-512", "rss", "rules", "sales", "save", "script", "sdk", "search", "secure", "security", "select", "services", "session", "sessions", "settings", "setup", "share", "shift", "shop", "signin", "signup", "site", "sitemap", "sites", "smtp", "sort", "source", "sql", "ssh", "ssh-rsa", "ssl", "ssladmin", "ssladministrator", "sslwebmaster", "stage", "staging", "stat", "static", "statistics", "stats", "status", "store", "style", "styles", "stylesheet", "stylesheets", "subdomain", "subscribe", "sudo", "super", "superuser", "support", "survey", "sync", "sysadmin", "system", "tablet", "tag", "tags", "team", "telnet", "terms", "terms-of-use", "test", "testimonials", "theme", "themes", "today", "tools", "topic", "topics", "tour", "training", "translate", "translations", "trending", "trial", "true", "umac-128", "umac-128-etm", "umac-64", "umac-64-etm", "undefined", "unfollow", "unsubscribe", "update", "upgrade", "usenet", "user", "username", "users", "uucp", "var", "verify", "video", "view", "void", "vote", "webmail", "webmaster", "website", "widget", "widgets", "wiki", "wpad", "write", "www", "www-data", "www1", "www2", "www3", "www4", "you", "yourname", "yourusername", "zlib"
]

# SESSION_COOKIE_AGE = 7

LOGIN_URL = "/account/login/"
LOGOUT_URL = "/account/logout/"

ROOT_URLCONF = "dopepod.urls"

SESSION_COOKIE_NAME = "sessionid"
#SESSION_COOKIE_DOMAIN = local_settings.SESSION_COOKIE_DOMAIN"

SESSION_COOKIE_SECURE = False
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# SOCIALACCOUNT_PROVIDERS = {
#     "github": {
#         "SCOPE": [
#             "user",
#             "repo",
#             "read:org",
#         ],
#     }
# }

SOCIALACCOUNT_PROVIDERS = {
     "facebook": {
         "METHOD": "oauth2",
         "SCOPE": ["email", "public_profile",],
         "AUTH_PARAMS": {"auth_type": "reauthenticate"},
         "INIT_PARAMS": {"cookie": True},
         "FIELDS": [
             "id",
             "email",
             "name",
             "first_name",
             "last_name",
             "verified",
             "locale",
             "timezone",
             "link",
             "gender",
             "updated_time",
             "friends",
         ],
         "EXCHANGE_TOKEN": True,
         "LOCALE_FUNC": lambda request: "en_US",
         "VERIFIED_EMAIL": True,
         "VERSION": "v2.12",
    },
    "google": {
        "SCOPE": ["profile", "email",],
        "AUTH_PARAMS": {"access_type": "online",},
        "VERIFIED_EMAIL": True,
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                ("django.template.loaders.cached.Loader", [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ]),
            ],
        },
    },
]

WSGI_APPLICATION = "dopepod.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = local_settings.DATABASES

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

# STATICFILES_DIRS =
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = "sgbackend.SendGridBackend"
SENDGRID_API_KEY = local_settings.SENDGRID_API_KEY
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = local_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = local_settings.EMAIL_HOST_PASSWORD
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = "noreply@dopepod.me"

# Email Configuration ==========================================================
#ADMINS = [("Me", "my@email"), ]
#MANAGERS = ADMINS
#DEFAULT_FROM_EMAIL = "from@email"
#SERVER_EMAIL = "error_from@email"

# Logging Configuration ========================================================
LOGGING = local_settings.LOGGING
