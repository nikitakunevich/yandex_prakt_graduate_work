from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FilmWork',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('title', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
                ('creation_date', models.DateField(blank=True, null=True)),
                ('certificate', models.TextField(blank=True, null=True)),
                ('file_path', models.TextField(blank=True, null=True)),
                ('rating', models.FloatField(blank=True, null=True)),
                ('type', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'film_work',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'genre',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GenreFilmWork',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('film_work', models.UUIDField(db_column='film_work_id')),
                ('genre', models.UUIDField(db_column='genre_id')),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'genre_film_work',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('full_name', models.TextField()),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'person',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PersonFilmWork',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('film_work', models.UUIDField(db_column='film_work_id')),
                ('person', models.UUIDField(db_column='person_id')),
                ('role', models.TextField()),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'person_film_work',
                'managed': False,
            },
        ),
    ]
