from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension, BtreeGinExtension


class Migration(migrations.Migration):
    dependencies = [
        ('quote', '0001_initial'),
    ]

    operations = [
        TrigramExtension(),
        BtreeGinExtension(),
    ]
