# Generated by Django 5.2.4 on 2025-07-05 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packing_lists', '0010_add_sample_prices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='packinglist',
            name='custom_type',
        ),
        migrations.RemoveField(
            model_name='packinglist',
            name='type',
        ),
        migrations.AddField(
            model_name='packinglist',
            name='custom_event_type',
            field=models.CharField(blank=True, help_text="If 'Other/Custom', specify type", max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='packinglist',
            name='direct_url',
            field=models.URLField(blank=True, help_text='Direct URL to the official or source list', null=True),
        ),
        migrations.AddField(
            model_name='packinglist',
            name='event_type',
            field=models.CharField(choices=[('school', 'School'), ('training', 'Training'), ('deployment', 'Deployment'), ('other', 'Other/Custom')], default='school', help_text='Type of event this list is for.', max_length=20),
        ),
        migrations.AddField(
            model_name='packinglist',
            name='last_updated',
            field=models.CharField(blank=True, help_text='Last update (YYYY, YYYY-MM, or YYYY-MM-DD)', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='packinglist',
            name='uploaded_file',
            field=models.FileField(blank=True, help_text='Upload a file for this list (CSV, Excel, PDF, etc.)', null=True, upload_to='packing_list_uploads/'),
        ),
        migrations.AlterField(
            model_name='packinglist',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Packing List Name'),
        ),
    ]
