
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingrecord',
            name='teacher',
            field=models.CharField(blank=True, max_length=50, verbose_name='授课传承人'),
        ),
    ]
