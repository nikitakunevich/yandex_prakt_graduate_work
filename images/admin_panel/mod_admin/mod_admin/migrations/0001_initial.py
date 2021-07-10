# Generated by Django 3.2.5 on 2021-07-09 07:48

import uuid

import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MovieFile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField(verbose_name="название")),
                (
                    "created_at",
                    model_utils.fields.AutoCreatedField(
                        blank=True,
                        default=django.utils.timezone.now,
                        editable=False,
                        null=True,
                        verbose_name="время создания",
                    ),
                ),
                (
                    "file_path",
                    models.FilePathField(verbose_name="путь к файлу с видео"),
                ),
            ],
        ),
    ]
