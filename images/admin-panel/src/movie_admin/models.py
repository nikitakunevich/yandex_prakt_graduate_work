import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoLastModifiedField, AutoCreatedField


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(_('название'))
    description = models.TextField(_('описание'), blank=True, null=True)
    created_at = AutoCreatedField(_('время создания'), blank=True, null=True)
    updated_at = AutoLastModifiedField(_('время последнего изменения'), blank=True, null=True)

    class Meta:
        db_table = 'genre'
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.name


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.TextField(_('полное имя'))
    birth_date = models.DateField(_('дата рождения'), blank=True, null=True)
    created_at = AutoCreatedField(_('время создания'), blank=True, null=True)
    updated_at = AutoLastModifiedField(_('время последнего изменения'), blank=True, null=True)

    class Meta:
        db_table = 'person'
        verbose_name = _('персона')
        verbose_name_plural = _('персоны')

    def __str__(self):
        return f"{self.full_name}"


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    SERIES = 'series', _('сериал')
    TV_SHOW = 'tv_show', _('шоу')


class MPAA_AgeRatingType(models.TextChoices):
    G = 'general', _('без ограничений')
    PG = 'parental_guidance', _('рекомендовано смотреть с родителями')
    PG_13 = 'parental_guidance_strong', _('просмотр не желателен детям до 13 лет')
    R = 'restricted', _('до 17 в сопровождении родителей')
    NC_17 = 'no_one_17_under', _('только с 18')


class FilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(_('название'))
    description = models.TextField(_('описание'), blank=True, null=True)
    creation_date = models.DateField(_('дата создания фильма'), blank=True, null=True)
    certificate = models.TextField(_('сертификат'), blank=True, null=True)
    file_path = models.FileField(_('путь к файлу с видео'), upload_to='assets/movies', blank=True, null=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True, null=True)
    type = models.TextField(_('тип'), blank=True, choices=FilmworkType.choices, null=True)
    mpaa_age_rating = models.TextField(_('возрастной рейтинг'), choices=MPAA_AgeRatingType.choices, blank=True,
                                       null=True)
    premium = models.BooleanField(_('премиум фильм'), default=True, blank=True, null=True)
    created_at = AutoCreatedField(_('время создания'), blank=True, null=True)
    updated_at = AutoLastModifiedField(_('время последнего изменения'), blank=True, null=True)

    genres = models.ManyToManyField(Genre, blank=True, through='GenreFilmWork')
    persons = models.ManyToManyField(Person, blank=True, through='PersonFilmWork')

    class Meta:
        db_table = 'film_work'
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self):
        return f"{self.title}"


class PersonRole(models.TextChoices):
    ACTOR = 'actor', _('актер')
    DIRECTOR = 'director', _('режиссер')
    WRITER = 'writer', _('сценарист')


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey(FilmWork, on_delete=models.deletion.CASCADE, verbose_name=_('фильм'))
    person = models.ForeignKey(Person, on_delete=models.deletion.CASCADE, verbose_name=_('человек'))
    role = models.TextField(_('кем работал на фильме'), choices=PersonRole.choices)
    created_at = AutoCreatedField(_('время создания'), blank=True, null=True)

    class Meta:
        db_table = 'person_film_work'
        verbose_name = _('участник фильма')
        verbose_name_plural = _('участники фильмов')
        unique_together = ['film_work', 'person', 'role']

    def __str__(self):
        return f"{self.person} in {self.film_work} as {self.role}"


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey(FilmWork, on_delete=models.deletion.CASCADE, verbose_name=_('фильм'))
    genre = models.ForeignKey(Genre, on_delete=models.deletion.CASCADE, verbose_name=_('жанр'))
    created_at = AutoCreatedField(_('время создания'), blank=True, null=True)

    class Meta:
        db_table = 'genre_film_work'
        verbose_name = _('жанр фильма')
        verbose_name_plural = _('жанры фильмов')
        unique_together = ['film_work', 'genre']

    def __str__(self):
        return f"{self.film_work} as {self.genre}"
