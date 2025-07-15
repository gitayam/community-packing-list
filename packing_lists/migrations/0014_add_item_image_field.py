# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packing_lists', '0013_add_security_fields_to_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, help_text='Upload an image of the item', null=True, upload_to='item_images/'),
        ),
    ] 