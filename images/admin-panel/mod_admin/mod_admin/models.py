import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class MovieFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(_("название"))
    created_at = AutoCreatedField(_("время создания"), blank=True, null=True)
    file_path = models.FileField(_("путь к файлу с видео"), upload_to="assets/movies")
