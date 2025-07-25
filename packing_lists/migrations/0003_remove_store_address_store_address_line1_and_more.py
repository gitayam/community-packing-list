# Generated by Django 5.2.4 on 2025-07-05 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("packing_lists", "0002_vote_created_at_vote_ip_address"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="store",
            name="address",
        ),
        migrations.AddField(
            model_name="store",
            name="address_line1",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="store",
            name="address_line2",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="store",
            name="city",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="store",
            name="country",
            field=models.CharField(
                blank=True, default="USA", max_length=100, null=True
            ),
        ),
        migrations.AddField(
            model_name="store",
            name="full_address_legacy",
            field=models.TextField(
                blank=True,
                help_text="For unstructured or imported addresses.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="store",
            name="latitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="store",
            name="longitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="store",
            name="state",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="store",
            name="zip_code",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
