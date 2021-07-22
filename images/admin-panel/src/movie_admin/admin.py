from django.contrib import admin

from movie_admin.models import FilmWork, PersonFilmWork, Genre, Person, GenreFilmWork


class PersonRoleInline(admin.TabularInline):
    model = PersonFilmWork
    fields = ('film_work', 'person', 'role')
    autocomplete_fields = ('person', 'film_work')
    extra = 0


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    fields = ('film_work', 'genre')
    autocomplete_fields = ('genre',)
    extra = 0


@admin.register(FilmWork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating', 'premium')
    list_filter = ('type', 'rating')
    search_fields = ('title', 'description', 'id')

    fields = ('title', 'type', 'description', 'creation_date', 'certificate',
              'file_path', 'mpaa_age_rating', 'rating', 'premium')

    inlines = [
        GenreFilmWorkInline,
        PersonRoleInline
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date')
    search_fields = ('full_name',)
    inlines = [
        PersonRoleInline
    ]
