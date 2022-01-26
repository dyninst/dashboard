__version__ = "0.0.1"
AUTHOR = "Vanessa Sochat"
AUTHOR_EMAIL = "vsoch@noreply.users.github.com"
NAME = "dyninst-dashboard"
PACKAGE_URL = "https://github.com/dyninst/dashboard"
KEYWORDS = "monitoring server for dyninst tests"
DESCRIPTION = "Dyninst Dashboard"
LICENSE = "LICENSE"

################################################################################
# Global requirements

# TODO freeze reqs when know working set

INSTALL_REQUIRES = (
    ("pyaml", {"min_version": "20.4.0"}),
    ("Jinja2", {"min_version": "2.11.2"}),
    ("Django", {"min_version": "3.0.8"}),
    ("django-crispy-forms", {"min_version": "1.10.0"}),
    ("django-taggit", {"min_version": "1.3.0"}),
    ("django-gravatar2", {"min_version": None}),
    ("django-ratelimit", {"min_version": "3.0.0"}),
    ("django-extensions", {"min_version": "3.0.2"}),
    ("djangorestframework", {"min_version": None}),
    ("django-rest-swagger", {"min_version": None}),
    ("drf-yasg", {"min_version": None}),
    ("psycopg2-binary", {"min_version": None}),
    # For nicer interactive shell
    ("ipython", {"min_version": None}),
    ("whitenoise", {"min_version": None}),
    ("pandas", {"min_version": None}),
    ("pyjwt", {"min_version": None}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

ALL_REQUIRES = INSTALL_REQUIRES
