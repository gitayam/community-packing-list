# Generated manually for sharing functionality
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('packing_lists', '0015_auto_20250806_0527'),
    ]

    operations = [
        # Add sharing fields to PackingList
        migrations.AddField(
            model_name='packinglist',
            name='is_public',
            field=models.BooleanField(default=True, help_text='Allow this list to be shared publicly'),
        ),
        migrations.AddField(
            model_name='packinglist',
            name='share_slug',
            field=models.SlugField(blank=True, max_length=100, null=True, unique=True, help_text='Unique URL slug for sharing'),
        ),
        migrations.AddField(
            model_name='packinglist',
            name='view_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of times this list has been viewed'),
        ),
        migrations.AddField(
            model_name='packinglist',
            name='created_at',
            field=models.DateTimeField(default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='packinglist',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]