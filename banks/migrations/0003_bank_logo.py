# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banks', '0002_alter_bank_code_alter_bank_contact_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='bank_logos/%Y/%m/%d/'),
        ),
    ]
