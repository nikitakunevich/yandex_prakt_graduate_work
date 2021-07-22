from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MoviesConfig(AppConfig):
    name = 'movie_admin'
    verbose_name = _('Фильмы')
