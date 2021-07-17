from django.contrib import admin
from mod_admin.models import MovieFile


@admin.register(MovieFile)
class MovieFileAdmin(admin.ModelAdmin):
    pass
