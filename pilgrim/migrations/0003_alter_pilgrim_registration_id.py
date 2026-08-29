# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pilgrim', '0002_alter_pilgrim_postal_code_alter_pilgrim_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pilgrim',
            name='registration_id',
            field=models.CharField(blank=True, db_index=True, max_length=20, unique=True),
        ),
    ]
