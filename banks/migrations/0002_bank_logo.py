# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='bank_logos/%Y/%m/%d/'),
        ),
    ]
