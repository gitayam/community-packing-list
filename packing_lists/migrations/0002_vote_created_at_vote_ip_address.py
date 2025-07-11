# Generated by Django 5.2.4 on 2025-07-05 01:12

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("packing_lists", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="vote",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="vote",
            name="ip_address",
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]
