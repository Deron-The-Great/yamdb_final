import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from reviews.models import Category, Genre, Title, Review, Comments, User

CSV_FILES_AND_MODELS = [
    ("category.csv", Category),
    ("genre.csv", Genre),
    ("titles.csv", Title),
    ("users.csv", User),
    ("genre_title.csv", Title.genre.through),
    ("review.csv", Review),
    ("comments.csv", Comments),
]


class Command(BaseCommand):
    help = 'Import data to database from csv.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--clear',
            action='store_true',
            default=False,
            help='Clear database before import.'
        )

    def handle(self, *args, **kwargs):
        for file, model in CSV_FILES_AND_MODELS:
            if kwargs['clear']:
                print(f'Deleting: {model}.')
                model.objects.all().delete()
                print(f'{model} has been deleted.')
            else:
                print(f'Importing: {model} from {file}.')
                import_from_csv(
                    os.path.join(settings.DATA_IMPORT_LOCATION, file),
                    model
                )
                print(f'{model} has been imported.')


def import_from_csv(file_name, model):
    with open(file_name, 'r', encoding="utf8") as file:
        rows = sum(1 for line in csv.reader(file, delimiter=',')) - 1

    with open(file_name, 'r', encoding="utf8") as file:
        csv_reader = csv.reader(file, delimiter=',')
        field_names = next(csv_reader)
        for i, field_name in enumerate(field_names):
            if (
                model._meta.get_field(field_name).is_relation
                and not field_name.endswith("_id")
            ):
                field_names[i] += "_id"

        for i, row in enumerate(csv_reader):
            item = {field: row[i] for i, field in enumerate(field_names)}
            name, created = model.objects.get_or_create(**item)
            print(f'[{i+1}/{rows}] Item {name} has been imported.')
